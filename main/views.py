from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.db.models import Q
import json
from datetime import datetime

from .models import Expense
from .serializers import SignUpSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.db.models import Sum

# ユーザー登録
class SignUpView(APIView):

    permission_classes = [] 

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        print(serializer.errors)

        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
                user=request.user,  # 🔑ここが重要
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
            return HttpResponseBadRequest(f"Invalid data: {str(e)}")


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

from django.db import models
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import Friend

# フレンド一覧取得
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def friend_list(request):
    user = request.user
    friends_qs = Friend.objects.filter(
        (models.Q(from_user=user) | models.Q(to_user=user)) & models.Q(accepted=True)
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
        return Response({'error': 'to_user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    if int(to_user_id) == from_user.id:
        return Response({'error': 'Cannot send friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # 既に申請や友達関係がないか確認
    if Friend.objects.filter(from_user=from_user, to_user=to_user).exists() or \
       Friend.objects.filter(from_user=to_user, to_user=from_user).exists():
        return Response({'error': 'Friend request already exists or you are already friends'}, status=status.HTTP_400_BAD_REQUEST)
    friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user, status='pending')

    return Response({'message': 'Friend request sent'})


# フレンド申請承認
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def accept_friend_request(request):
    user = request.user
    from_user_id = request.data.get('from_user_id')

    if not from_user_id:
        return Response({'error': 'from_user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        friend_request = Friend.objects.get(from_user_id=from_user_id, to_user=user, accepted=False)
    except Friend.DoesNotExist:
        return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

    friend_request.accepted = True
    friend_request.save()
    return Response({'message': 'Friend request accepted'})


# フレンド申請拒否または削除
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def remove_friend(request):
    user = request.user
    other_user_id = request.data.get('user_id')

    if not other_user_id:
        return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    friend = Friend.objects.filter(
        (models.Q(from_user=user, to_user_id=other_user_id) |
         models.Q(from_user_id=other_user_id, to_user=user))
    )
    deleted_count, _ = friend.delete()

    if deleted_count == 0:
        return Response({'error': 'Friend relationship not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'message': 'Friend removed or request canceled'})
from django.contrib.auth.models import User


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_search(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return Response([])

    # usernameに部分一致で検索、かつ自分自身は除外
    users = User.objects.filter(username__icontains=q).exclude(id=request.user.id)
    data = [{"id": u.id, "username": u.username} for u in users]
    return Response(data)


from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import FriendRequest

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


    



from .models import FriendRequest, Friend  # ← Friend を忘れずインポート

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
            # 承認処理
            fr.status = 'accepted'
            fr.save()

            # 双方向のFriend関係を作成
            Friend.objects.create(from_user=fr.from_user, to_user=fr.to_user, accepted=True)
        else:
            # 拒否処理
            fr.status = 'rejected'
            fr.save()

        return Response({"message": "処理が完了しました"})



@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def friend_expenses(request, friend_id):
    user = request.user
    from .models import Friend, Expense
    from django.db.models import Q

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


from django.http import HttpResponse
from django.contrib.auth import get_user_model

def create_admin(request):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'yourpassword123')
        return HttpResponse("Admin created!")
    else:
        return HttpResponse("Admin already exists.")
