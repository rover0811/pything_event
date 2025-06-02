from typing import TYPE_CHECKING
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ValidationError

from users.services import user_create, user_update, user_approve
from users.selectors import user_list, user_get, user_get_pending_approval

if TYPE_CHECKING:
    from users.models import User
else:
    from django.contrib.auth import get_user_model

    User = get_user_model()


class UserCreateApi(APIView):
    permission_classes = [AllowAny]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        name = serializers.CharField(max_length=100)
        password = serializers.CharField(min_length=8)
        phone = serializers.CharField(max_length=20, required=False)
        company = serializers.CharField(max_length=100, required=False)
        newsletter_subscribed = serializers.BooleanField(default=False)
        referrer_id = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()
        name = serializers.CharField()
        user_type = serializers.CharField()
        date_joined = serializers.DateTimeField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = user_create(**serializer.validated_data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # OutputSerializer로 응답 데이터 직렬화
        output_serializer = self.OutputSerializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class UserListApi(APIView):
    """사용자 목록 API"""
    permission_classes = [IsAuthenticated]

    class FilterSerializer(serializers.Serializer):
        user_type = serializers.ChoiceField(
            choices=User.UserType.choices,
            required=False
        )
        newsletter_subscribed = serializers.BooleanField(required=False)
        search = serializers.CharField(required=False)
        has_referrer = serializers.BooleanField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()
        name = serializers.CharField()
        company = serializers.CharField()
        user_type = serializers.CharField()
        newsletter_subscribed = serializers.BooleanField()
        referrer_name = serializers.CharField(source='referrer.name', allow_null=True)
        date_joined = serializers.DateTimeField()

    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        users = user_list(filters=filters_serializer.validated_data)

        # OutputSerializer로 응답 데이터 직렬화
        data = self.OutputSerializer(users, many=True).data
        return Response(data)


class UserDetailApi(APIView):
    """사용자 상세 조회 API"""
    permission_classes = [IsAuthenticated]

    # GET은 입력이 URL parameter뿐이므로 InputSerializer 없음
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()
        name = serializers.CharField()
        phone = serializers.CharField()
        company = serializers.CharField()
        user_type = serializers.CharField()
        newsletter_subscribed = serializers.BooleanField()
        referrer_name = serializers.CharField(source='referrer.name', allow_null=True)
        approved_by_name = serializers.CharField(source='approved_by.name', allow_null=True)
        date_joined = serializers.DateTimeField()
        updated_at = serializers.DateTimeField()

        # 모델 속성도 직렬화 가능
        is_approved_member = serializers.BooleanField()
        full_display_name = serializers.CharField()

    def get(self, request, user_id):
        user = user_get(user_id=user_id)

        # OutputSerializer로 응답 데이터 직렬화
        data = self.OutputSerializer(user).data
        return Response(data)


class UserUpdateApi(APIView):
    """사용자 정보 수정 API"""
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100, required=False)
        phone = serializers.CharField(max_length=20, required=False)
        company = serializers.CharField(max_length=100, required=False)
        newsletter_subscribed = serializers.BooleanField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        phone = serializers.CharField()
        company = serializers.CharField()
        newsletter_subscribed = serializers.BooleanField()
        updated_at = serializers.DateTimeField()

    def patch(self, request, user_id):
        user = user_get(user_id=user_id)

        # 간단한 권한 체크 (본인만 수정 가능)
        if user != request.user:
            return Response(
                {'error': '본인의 정보만 수정할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_user = user_update(user=user, data=serializer.validated_data)

        # OutputSerializer로 응답 데이터 직렬화
        output_serializer = self.OutputSerializer(updated_user)
        return Response(output_serializer.data)


class UserApproveApi(APIView):
    """사용자 승인 API"""
    permission_classes = [IsAuthenticated]

    # POST이지만 body 데이터가 없으므로 InputSerializer 없음
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        email = serializers.EmailField()
        user_type = serializers.CharField()
        approved_by_name = serializers.CharField(source='approved_by.name')

    def post(self, request, user_id):
        if request.user.user_type != User.UserType.ADMIN:
            return Response(
                {'error': '어드민 권한이 필요합니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user = user_get(user_id=user_id)
        approved_user = user_approve(user=user, approved_by=request.user)

        # OutputSerializer로 응답 데이터 직렬화
        response_data = {
            **self.OutputSerializer(approved_user).data,
            'message': f'{approved_user.name}님이 정회원으로 승인되었습니다.'
        }

        return Response(response_data)


class UserPendingApprovalListApi(APIView):
    """승인 대기 사용자 목록 API"""
    permission_classes = [IsAuthenticated]

    # GET이므로 InputSerializer 없음
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        email = serializers.EmailField()
        company = serializers.CharField()
        referrer_name = serializers.CharField(source='referrer.name', allow_null=True)
        date_joined = serializers.DateTimeField()
        waiting_days = serializers.SerializerMethodField()

        def get_waiting_days(self, obj):
            from django.utils import timezone
            return (timezone.now().date() - obj.date_joined.date()).days

    def get(self, request):
        if request.user.user_type != User.UserType.ADMIN:
            return Response(
                {'error': '어드민 권한이 필요합니다.'},
                status=status.HTTP_403_FORBIDDEN
            )

        pending_users = user_get_pending_approval()

        # OutputSerializer로 응답 데이터 직렬화
        data = self.OutputSerializer(pending_users, many=True).data
        return Response(data)
