from django.urls import path, include
from users.apis import (
    UserCreateApi,
    UserListApi,
    UserDetailApi,
    UserUpdateApi,
    UserApproveApi,
    UserPendingApprovalListApi
)

from users.auth_apis import (
    LoginApi,
    LogoutApi,
    MeApi,
    CSRFTokenApi,
    ChangePasswordApi,
    CheckAuthApi
)

# Django Styleguide 패턴: 작업별 URL 분리
user_patterns = [
    path('', UserListApi.as_view(), name='list'),
    path('create/', UserCreateApi.as_view(), name='create'),
    path('pending-approval/', UserPendingApprovalListApi.as_view(), name='pending-approval'),
    path('<int:user_id>/', UserDetailApi.as_view(), name='detail'),
    path('<int:user_id>/update/', UserUpdateApi.as_view(), name='update'),
    path('<int:user_id>/approve/', UserApproveApi.as_view(), name='approve'),
]

# 인증 관련 URL 패턴
auth_patterns = [
    path('csrf/', CSRFTokenApi.as_view(), name='csrf-token'),
    path('login/', LoginApi.as_view(), name='login'),
    path('logout/', LogoutApi.as_view(), name='logout'),
    path('me/', MeApi.as_view(), name='me'),
    path('check/', CheckAuthApi.as_view(), name='check'),
    path('change-password/', ChangePasswordApi.as_view(), name='change-password'),
]

urlpatterns = [
    path('', include((user_patterns, 'users'))),  # 'users' namespace 추가
    path('auth/', include((auth_patterns, 'auth'))),  # 이 줄 추가!
]
