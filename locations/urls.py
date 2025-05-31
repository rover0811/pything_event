# location/urls.py
from django.urls import path, include
from .apis import (
    LocationCreateApi,
    LocationListApi,
    LocationDetailApi,
    LocationUpdateApi,
    LocationDeleteApi,
    LocationSuitableApi
)

# Django Styleguide 패턴: 작업별 URL 분리
location_patterns = [
    path('', LocationListApi.as_view(), name='list'),
    path('create/', LocationCreateApi.as_view(), name='create'),
    path('suitable/', LocationSuitableApi.as_view(), name='suitable'),
    path('<int:location_id>/', LocationDetailApi.as_view(), name='detail'),
    path('<int:location_id>/update/', LocationUpdateApi.as_view(), name='update'),
    path('<int:location_id>/delete/', LocationDeleteApi.as_view(), name='delete'),
]

urlpatterns = [
    path('', include((location_patterns, 'locations'))),  # 'locations' namespace 추가
]