# main/serializers.py
from rest_framework import serializers
from .models import Expense
from django.contrib.auth.models import User
from rest_framework import serializers




from rest_framework import serializers
from .models import Expense
from django.contrib.auth.models import User


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'



class SignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user
    


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ExpenseSerializer(serializers.ModelSerializer):
    shared_with = UserSerializer(many=True, read_only=True)  # 共有ユーザーの情報を表示
    shared_with_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, source='shared_with'
    )  # 更新用フィールド（ユーザーIDで共有設定）

    class Meta:
        model = Expense
        fields = '__all__'  # もしくは ['id', ..., 'shared_with', 'shared_with_ids'] に変更可
