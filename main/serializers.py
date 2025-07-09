from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Expense

# Expense シリアライザ
class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = '__all__'

# ユーザー登録用シリアライザ
class SignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True, label="確認用パスワード")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
        extra_kwargs = {
            'username': {
                'required': True,
                'error_messages': {
                    'required': 'ユーザー名は必須です。',
                    'unique': 'このユーザー名は既に使われています。',
                }
            },
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'メールアドレスは必須です。',
                    'unique': 'このメールアドレスは既に使われています。',
                }
            },
            'password': {
                'write_only': True,
                'required': True,
                'error_messages': {
                    'required': 'パスワードは必須です。',
                }
            },
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'パスワードが一致しません。'})
        return data

    def validate_password(self, value):
        validate_password(value)
        return value

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
