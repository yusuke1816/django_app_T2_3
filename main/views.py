from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum
import json
from datetime import datetime

from .models import Expense, FriendRequest, Friend
from .serializers import SignUpSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# ユーザー登録
class SignUpView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'ユーザー登録に成功しました'}, status=status.HTTP_201_CREATED)

        # ここを変更
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 支出の取得・登録
@api_view(["GET", "POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def expenses_list(request):
    if request.method == "GET":
        q = request.GET.get("q", "").strip()
        if q:
            expenses = Expense.objects.filter(
                Q(title__icontains=q) |
                Q(category__icontains=q),
                user=request.user
            )
        else:
            expenses = Expense.objects.filter(user=request.user)

        expense_list = [
            {
                "id": e.id,
                "title": e.title,
                "amount": str(e.amount),
                "currency": e.currency,
                "category": e.category,
                "date": e.date.isoformat(),
            }
            for e in expenses
        ]
        return JsonResponse(expense_list, safe=False)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()

            expense = Expense.objects.create(
                user=request.user,
                title=data['title'],
                amount=data['amount'],
                currency=data.get('currency', 'JPY'),
                category=data['category'],
                date=date_obj,
            )
            return JsonResponse({
                "id": expense.id,
                "title": expense.title,
                "amount": str(expense.amount),
                "currency": expense.currency,
                "category": expense.category,
                "date": expense.date.isoformat()
            })

        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return HttpResponseBadRequest(f"不正なデータです: {str(e)}")

# 合計金額（JPYのみ）
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def total_jpy_expenses(request):
    total = Expense.objects.filter(user=request.user, currency='JPY').aggregate(total=Sum('amount'))['total'] or 0
    return JsonResponse({"totalAmount": float(total)})

# ユーザー情報取得API
class UserMeView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        })

# フレンド一覧取得
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def friend_list(request):
    user = request.user
    friends_qs = Friend.objects.filter(
        (Q(from_user=user) | Q(to_user=user)) & Q(accepted=True)
    )
    friends = []
    for f in friends_qs:
        friend_user = f.to_user if f.from_user == user else f.from_user
        friends.append({
            'id': friend_user.id,
            'username': friend_user.username,
        })
    return Response(friends)

# フレンド申請送信
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    from_user = request.user
    to_user_id = request.data.get('to_user_id')

    if not to_user_id:
        return Response({'error': 'to_user_idは必須です'}, status=status.HTTP_400_BAD_REQUEST)

    if int(to_user_id) == from_user.id:
        return Response({'error': '自分自身にフレンド申請はできません'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response({'error': 'ユーザーが存在しません'}, status=status.HTTP_404_NOT_FOUND)

    if Friend.objects.filter(from_user=from_user, to_user=to_user).exists() or \
       Friend.objects.filter(from_user=to_user, to_user=from_user).exists():
        return Response({'error': '既に申請済み、または友達関係です'}, status=status.HTTP_400_BAD_REQUEST)

    FriendRequest.objects.create(from_user=from_user, to_user=to_user, status='pending')
    return Response({'message': 'フレンド申請を送信しました'})

# フレンド申請承認
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def accept_friend_request(request):
    user = request.user
    from_user_id = request.data.get('from_user_id')

    if not from_user_id:
        return Response({'error': 'from_user_idは必須です'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        friend_request = Friend.objects.get(from_user_id=from_user_id, to_user=user, accepted=False)
    except Friend.DoesNotExist:
        return Response({'error': 'フレンド申請が見つかりません'}, status=status.HTTP_404_NOT_FOUND)

    friend_request.accepted = True
    friend_request.save()
    return Response({'message': 'フレンド申請を承認しました'})

# フレンド申請拒否または削除
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_friend(request):
    user = request.user
    other_user_id = request.data.get('user_id')

    if not other_user_id:
        return Response({'error': 'user_idは必須です'}, status=status.HTTP_400_BAD_REQUEST)

    friend = Friend.objects.filter(
        (Q(from_user=user, to_user_id=other_user_id) |
         Q(from_user_id=other_user_id, to_user=user))
    )
    deleted_count, _ = friend.delete()

    if deleted_count == 0:
        return Response({'error': 'フレンド関係が見つかりません'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'message': 'フレンドを削除または申請をキャンセルしました'})

# ユーザー検索
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_search(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return Response([])

    users = User.objects.filter(username__icontains=q).exclude(id=request.user.id)
    data = [{"id": u.id, "username": u.username} for u in users]
    return Response(data)

# 申請一覧取得
class FriendRequestsListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        requests = FriendRequest.objects.filter(to_user=user, status='pending')
        data = [
            {
                "id": fr.id,
                "from_user": {
                    "id": fr.from_user.id,
                    "username": fr.from_user.username,
                }
            }
            for fr in requests
        ]
        return Response(data)

# フレンド申請の承認・拒否
class RespondFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        try:
            fr = FriendRequest.objects.get(id=request_id, to_user=request.user, status='pending')
        except FriendRequest.DoesNotExist:
            return Response({"error": "申請が存在しません"}, status=status.HTTP_400_BAD_REQUEST)

        accept = request.data.get("accept")
        if accept is None:
            return Response({"error": "acceptフィールドが必要です"}, status=status.HTTP_400_BAD_REQUEST)

        if accept:
            fr.status = 'accepted'
            fr.save()
            Friend.objects.create(from_user=fr.from_user, to_user=fr.to_user, accepted=True)
        else:
            fr.status = 'rejected'
            fr.save()

        return Response({"message": "処理が完了しました"})

# フレンドの支出一覧取得
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def friend_expenses(request, friend_id):
    user = request.user

    # フレンド関係かどうか確認
    is_friend = Friend.objects.filter(
        Q(from_user=user, to_user_id=friend_id, accepted=True) |
        Q(from_user_id=friend_id, to_user=user, accepted=True)
    ).exists()

    if not is_friend:
        return Response({'error': 'フレンド関係がありません'}, status=403)

    expenses = Expense.objects.filter(user_id=friend_id)
    data = [
        {
            'id': e.id,
            'title': e.title,
            'amount': str(e.amount),
            'category': e.category,
            'date': e.date.isoformat()
        }
        for e in expenses
    ]
    return Response(data)

# 管理者作成
def create_admin(request):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'yourpassword123')
        return HttpResponse("管理者を作成しました！")
    else:
        return HttpResponse("管理者はすでに存在します。")



@api_view(["DELETE"])
@authentication_classes([JWTAuthentication])  # または TokenAuthentication
@permission_classes([IsAuthenticated])
def expense_detail(request, pk):
    try:
        expense = Expense.objects.get(pk=pk, user=request.user)
    except Expense.DoesNotExist:
        return Response({"detail": "対象の支出が見つかりません。"}, status=status.HTTP_404_NOT_FOUND)

    expense.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)