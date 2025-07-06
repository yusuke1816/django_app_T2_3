from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView
from django.urls import path
from .views import SignUpView
urlpatterns = [
    path('expenses/', views.expenses_list, name='expenses-list'),
    path('expenses/total-jpy/', views.total_jpy_expenses, name='total-jpy-expenses'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
     path('auth/signup/', SignUpView.as_view(), name='signup'),
]

