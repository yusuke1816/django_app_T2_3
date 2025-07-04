from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Expense
from datetime import datetime

@csrf_exempt
@require_http_methods(["GET", "POST"])
def expenses_list(request):
    if request.method == "GET":
        expenses = list(Expense.objects.values())
        return JsonResponse(expenses, safe=False)
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()  # 文字列→日付に変換

            expense = Expense.objects.create(
                title=data['title'],
                amount=data['amount'],
                category=data['category'],
                date=date_obj,
            )
            return JsonResponse({
                "id": expense.id,
                "title": expense.title,
                "amount": str(expense.amount),
                "category": expense.category,
                "date": expense.date.isoformat()
            })
        except (KeyError, json.JSONDecodeError, ValueError) as e:
            return HttpResponseBadRequest(f"Invalid data: {str(e)}")
