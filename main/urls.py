from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import friend_expenses 
from .views import UserMeView  # ← 追加
from .views import create_admin
urlpatterns = [
    path('expenses/', views.expenses_list, name='expenses-list'),
    path('expenses/total-jpy/', views.total_jpy_expenses, name='total-jpy-expenses'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/signup/', views.SignUpView.as_view(), name='signup'),
    path('users/me/', UserMeView.as_view(), name='user-me'),  # ← 追加
    path('friends/', views.friend_list),                      # GETでフレンド一覧取得
    path('friends/request/', views.send_friend_request),       # POSTでフレンド申請
    path('users/search/', views.user_search, name='user_search'),
    path('friends/requests/', views.FriendRequestsListView.as_view(), name='friend_requests_list'),
    path('friends/request/<int:request_id>/respond/', views.RespondFriendRequestView.as_view(), name='respond_friend_request'),
    path('friends/<int:friend_id>/expenses/', friend_expenses, name='friend-expenses'),
    # 他のURLも同様に
      path('create-admin/', create_admin),  # ←
]


