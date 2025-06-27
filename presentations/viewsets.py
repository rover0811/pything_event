from django.http import FileResponse, Http404, HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import PresentationForm

from presentations.models import Presentation, PresentationComment
from presentations.serializers import PresentationSerializer, PresentationCommentSerializer
from users.models import User


class PresentationViewSet(viewsets.ModelViewSet):
    queryset = Presentation.objects.select_related('presenter', 'event').prefetch_related('comments')
    serializer_class = PresentationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # 정회원만 발표 신청 가능
        if self.request.user.user_type != User.UserType.REGULAR:
            raise PermissionDenied('정회원만 발표를 신청할 수 있습니다.')
        serializer.save()

    def perform_update(self, serializer):
        presentation = self.get_object()
        # 발표자 본인 또는 어드민만 수정 가능
        if (presentation.presenter != self.request.user and
                self.request.user.user_type != User.UserType.ADMIN):
            raise PermissionDenied('발표자 본인만 수정할 수 있습니다.')
        serializer.save()

    def perform_destroy(self, instance):
        # 발표자 본인 또는 어드민만 삭제 가능
        if (instance.presenter != self.request.user and
                self.request.user.user_type != User.UserType.ADMIN):
            raise PermissionDenied('발표자 본인만 삭제할 수 있습니다.')
        instance.delete()

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def download(self, request, pk=None):
        """파일 다운로드"""
        presentation = self.get_object()

        if not presentation.file_url:
            raise Http404("파일이 없습니다.")

        try:
            response = FileResponse(
                presentation.file_url.open(),
                as_attachment=True,
                filename=presentation.file_name
            )
            return response
        except FileNotFoundError:
            raise Http404("파일을 찾을 수 없습니다.")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def select(self, request, pk=None):
        """발표 선정 (어드민만)"""
        if request.user.user_type != User.UserType.ADMIN:
            raise PermissionDenied('어드민 권한이 필요합니다.')

        presentation = self.get_object()
        presentation.status = Presentation.Status.SELECTED
        presentation.selected_for_newsletter = request.data.get('selected_for_newsletter', False)
        presentation.save()

        serializer = self.get_serializer(presentation)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        """발표 거절 (어드민만)"""
        if request.user.user_type != User.UserType.ADMIN:
            raise PermissionDenied('어드민 권한이 필요합니다.')

        presentation = self.get_object()
        presentation.status = Presentation.Status.REJECTED
        presentation.save()

        serializer = self.get_serializer(presentation)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def pending(self, request):
        """승인 대기 발표 목록 (어드민만)"""
        if request.user.user_type != User.UserType.ADMIN:
            raise PermissionDenied('어드민 권한이 필요합니다.')

        pending_presentations = self.queryset.filter(status=Presentation.Status.SUBMITTED)
        page = self.paginate_queryset(pending_presentations)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(pending_presentations, many=True)
        return Response(serializer.data)


class PresentationCommentViewSet(viewsets.ModelViewSet):
    queryset = PresentationComment.objects.select_related('user', 'presentation')
    serializer_class = PresentationCommentSerializer
    permission_classes = [AllowAny]  # 누구나 조회/생성 가능

    def perform_update(self, serializer):
        """수정 권한 확인"""
        comment = self.get_object()
        if not comment.can_edit(self.request.user):
            raise PermissionDenied("수정 권한이 없습니다.")
        serializer.save()

    def perform_destroy(self, instance):
        """삭제 권한 확인"""
        if not instance.can_delete(self.request.user):
            raise PermissionDenied("삭제 권한이 없습니다.")
        instance.delete()


class PresentationCreateView(LoginRequiredMixin, CreateView):
    model = Presentation
    form_class = PresentationForm
    template_name = 'presentation_form.html'
    success_url = reverse_lazy('presentations')

    def form_valid(self, form):
        if self.request.user.user_type != User.UserType.REGULAR:
            form.add_error(None, '정회원만 발표를 신청할 수 있습니다.')
            return self.form_invalid(form)
        form.instance.presenter = self.request.user
        messages.success(self.request, '발표가 성공적으로 등록되었습니다.')
        # AJAX 요청이면 리다이렉트하지 않고 200 OK만 반환
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            super().form_valid(form)  # 실제 저장
            return HttpResponse(status=200)
        return super().form_valid(form)

    def form_invalid(self, form):
        # AJAX 요청이면 폼 HTML만 반환
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = '발표 등록'
        return context