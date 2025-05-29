# users/urls.py
from django.urls import path, include
from .apis import (
    UserCreateApi,
    UserListApi,
    UserDetailApi,
    UserUpdateApi,
    UserApproveApi,
    UserPendingApprovalListApi
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

urlpatterns = [
    path('', include((user_patterns, 'users'))),  # 'users' namespace 추가
]