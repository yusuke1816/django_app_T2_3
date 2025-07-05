from django.db import models
from django.db.models import Sum

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('food', '食費'),
        ('transport', '交通費'),
        ('entertainment', '娯楽'),
        ('other', 'その他'),
    ]

    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='JPY')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.amount}円"

    @classmethod
    def total_jpy_amount(cls):
        return cls.objects.filter(currency='JPY').aggregate(total=Sum('amount'))['total'] or 0
