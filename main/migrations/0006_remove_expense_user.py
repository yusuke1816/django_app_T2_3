# Generated by Django 5.2.4 on 2025-07-06 05:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_expense_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expense',
            name='user',
        ),
    ]
