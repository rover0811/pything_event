from typing import TYPE_CHECKING
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from users.models import User
else:
    from django.contrib.auth import get_user_model

    User = get_user_model()


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenApi(APIView):
    """CSRF 토큰 발급 API"""
    permission_classes = [AllowAny]

    def get(self, request):
        token = get_token(request)
        return Response({'csrf_token': token})


class LoginApi(APIView):
    """로그인 API"""
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        username = serializers.CharField()
        password = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()
        username = serializers.CharField()
        user_type = serializers.CharField()
        newsletter_subscribed = serializers.BooleanField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # Django의 기본 authenticate 함수 사용
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {'error': '이메일 또는 비밀번호가 올바르지 않습니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': '비활성화된 계정입니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Django의 기본 login 함수 사용 (세션 생성)
        login(request, user)

        output_serializer = self.OutputSerializer(user)
        return Response({
            'user': output_serializer.data,
            'message': '로그인되었습니다.'
        })


class LogoutApi(APIView):
    """로그아웃 API"""

    def post(self, request):
        logout(request)  # Django의 기본 logout 함수 (세션 삭제)
        return Response({'message': '로그아웃되었습니다.'})


class MeApi(APIView):
    """현재 로그인한 사용자 정보 API"""

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()
        username = serializers.CharField()
        user_type = serializers.CharField()
        newsletter_subscribed = serializers.BooleanField()
        is_approved_member = serializers.BooleanField()
        full_display_name = serializers.CharField()

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': '인증되지 않은 사용자입니다.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = self.OutputSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordApi(APIView):
    """비밀번호 변경 API"""

    class InputSerializer(serializers.Serializer):
        current_password = serializers.CharField()
        new_password = serializers.CharField(min_length=8)
        confirm_password = serializers.CharField()

        def validate(self, data):
            if data['new_password'] != data['confirm_password']:
                raise serializers.ValidationError("새 비밀번호가 일치하지 않습니다.")
            return data

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        # 현재 비밀번호 확인
        if not user.check_password(current_password):
            return Response(
                {'error': '현재 비밀번호가 올바르지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 새 비밀번호 설정
        user.set_password(new_password)
        user.save()

        return Response({'message': '비밀번호가 변경되었습니다.'})


class CheckAuthApi(APIView):
    """인증 상태 확인 API (Next.js용)"""
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'authenticated': True,
                'user': {
                    'id': request.user.id,
                    'email': request.user.email,
                    'username': request.user.username,
                    'user_type': request.user.user_type,
                }
            })

        return Response({
            'authenticated': False,
            'user': None
        })