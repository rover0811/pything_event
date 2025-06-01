from rest_framework.routers import DefaultRouter
from presentations.viewsets import PresentationCommentViewSet

router = DefaultRouter()
router.register('comments', PresentationCommentViewSet, basename='presentation-comments')

urlpatterns = router.urls
