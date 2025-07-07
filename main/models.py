from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('food', '食費'),
        ('transport', '交通費'),
        ('entertainment', '娯楽'),
        ('other', 'その他'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')

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

# フレンド機能用モデル
class Friend(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_received')
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        status = 'Accepted' if self.accepted else 'Pending'
        return f"{self.from_user.username} -> {self.to_user.username} ({status})"


from django.db import models
from django.contrib.auth.models import User

class FriendRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '未処理'),
        ('accepted', '承認済み'),
        ('rejected', '拒否済み'),
    ]

    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
