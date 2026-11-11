"""Authentication, profile, and user-management routes."""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from .views import (
    RegisterView,
    ProfileView,
    UserListView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),

    path('login/', TokenObtainPairView.as_view(), name='login'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User management
    path('profile/', ProfileView.as_view(), name='profile'),

    path('users/', UserListView.as_view(), name='user_list'),
]
