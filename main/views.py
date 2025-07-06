from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q
import json
from .models import Expense
from datetime import datetime


# main/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignUpSerializer

class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def expenses_list(request):
    if request.method == "GET":
        q = request.GET.get("q", "").strip()
        if q:
            expenses = Expense.objects.filter(
                Q(title__icontains=q) |
                Q(category__icontains=q)
            )
        else:
            expenses = Expense.objects.all()

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


# 🧮 合計を返すAPI
@require_http_methods(["GET"])
def total_jpy_expenses(request):
    total = Expense.total_jpy_amount()
    return JsonResponse({"totalAmount": float(total)})
