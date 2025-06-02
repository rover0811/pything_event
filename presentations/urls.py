from rest_framework.routers import DefaultRouter
from presentations.viewsets import PresentationCommentViewSet, PresentationViewSet

router = DefaultRouter()
router.register('presentations', PresentationViewSet)
router.register('comments', PresentationCommentViewSet, basename='presentation-comments')

urlpatterns = router.urls
