from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from presentations.models import PresentationComment
from presentations.serializers import PresentationCommentSerializer


class PresentationCommentViewSet(viewsets.ModelViewSet):
    queryset = PresentationComment.objects.all()
    serializer_class = PresentationCommentSerializer
    permission_classes = [AllowAny]

    def perform_update(self, serializer):
        comment = self.get_object()
        if not comment.user or comment.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("회원 댓글만 수정 가능하고, 본인 댓글만 수정할 수 있습니다.")
        serializer.save()

    def perform_destroy(self, instance):
        if not instance.user or instance.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("회원 댓글만 삭제 가능하고, 본인 댓글만 삭제할 수 있습니다.")
        instance.delete()
