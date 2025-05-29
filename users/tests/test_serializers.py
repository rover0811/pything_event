"""
시리얼라이저 테스트
Django Styleguide: 시리얼라이저는 유효성 검사와 직렬화/역직렬화를 테스트
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserCreateInputSerializer:
    """사용자 생성 입력 시리얼라이저 테스트"""

    def test_valid_data(self):
        """유효한 데이터 검증"""
        from users.apis import UserCreateApi

        data = {
            'email': 'test@example.com',
            'name': '테스트',
            'password': 'testpass123',
            'phone': '010-1234-5678',
            'company': '테스트 회사',
            'newsletter_subscribed': True
        }

        serializer = UserCreateApi.InputSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == data['email']
        assert serializer.validated_data['name'] == data['name']
        assert serializer.validated_data['password'] == data['password']

    def test_invalid_email(self):
        """잘못된 이메일 검증"""
        from users.apis import UserCreateApi

        data = {
            'email': 'invalid-email',
            'name': '테스트',
            'password': 'testpass123'
        }

        serializer = UserCreateApi.InputSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_short_password(self):
        """짧은 비밀번호 검증"""
        from users.apis import UserCreateApi

        data = {
            'email': 'test@example.com',
            'name': '테스트',
            'password': '123'
        }

        serializer = UserCreateApi.InputSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors


@pytest.mark.django_db
class TestUserListFilterSerializer:
    """사용자 목록 필터 시리얼라이저 테스트"""

    def test_valid_filters(self):
        """유효한 필터 검증"""
        from users.apis import UserListApi

        data = {
            'user_type': 'NON_MEMBER',
            'newsletter_subscribed': True,
            'search': '테스트',
            'has_referrer': True
        }

        serializer = UserListApi.FilterSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['user_type'] == data['user_type']
        assert serializer.validated_data['newsletter_subscribed'] == data['newsletter_subscribed']

    def test_invalid_user_type(self):
        """잘못된 사용자 타입 검증"""
        from users.apis import UserListApi

        data = {
            'user_type': 'INVALID_TYPE'
        }

        serializer = UserListApi.FilterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'user_type' in serializer.errors


@pytest.mark.django_db
class TestUserUpdateInputSerializer:
    """사용자 정보 수정 입력 시리얼라이저 테스트"""

    def test_valid_data(self):
        """유효한 데이터 검증"""
        from users.apis import UserUpdateApi

        data = {
            'name': '새이름',
            'phone': '010-9999-8888',
            'company': '새회사',
            'newsletter_subscribed': True
        }

        serializer = UserUpdateApi.InputSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['name'] == data['name']
        assert serializer.validated_data['phone'] == data['phone']

    def test_empty_data(self):
        """빈 데이터 검증"""
        from users.apis import UserUpdateApi

        data = {}

        serializer = UserUpdateApi.InputSerializer(data=data)
        assert serializer.is_valid()  # 모든 필드가 선택적이므로 빈 데이터도 유효함


@pytest.mark.django_db
class TestUserOutputSerializers:
    """사용자 출력 시리얼라이저 테스트"""

    def test_user_create_output_serializer(self):
        """사용자 생성 출력 시리얼라이저 테스트"""
        from users.apis import UserCreateApi

        user = UserFactory()
        serializer = UserCreateApi.OutputSerializer(user)

        assert serializer.data['id'] == user.id
        assert serializer.data['email'] == user.email
        assert serializer.data['name'] == user.name
        assert serializer.data['user_type'] == user.user_type
        assert 'date_joined' in serializer.data

    def test_user_list_output_serializer(self):
        """사용자 목록 출력 시리얼라이저 테스트"""
        from users.apis import UserListApi

        user = UserFactory()
        serializer = UserListApi.OutputSerializer(user)

        assert serializer.data['id'] == user.id
        assert serializer.data['email'] == user.email
        assert serializer.data['name'] == user.name
        assert serializer.data['company'] == user.company
        assert serializer.data['user_type'] == user.user_type
        assert serializer.data['newsletter_subscribed'] == user.newsletter_subscribed
        assert 'referrer_name' in serializer.data
        assert 'date_joined' in serializer.data

    def test_user_detail_output_serializer(self):
        """사용자 상세 출력 시리얼라이저 테스트"""
        from users.apis import UserDetailApi

        user = UserFactory()
        serializer = UserDetailApi.OutputSerializer(user)

        assert serializer.data['id'] == user.id
        assert serializer.data['email'] == user.email
        assert serializer.data['name'] == user.name
        assert serializer.data['phone'] == user.phone
        assert serializer.data['company'] == user.company
        assert serializer.data['user_type'] == user.user_type
        assert serializer.data['newsletter_subscribed'] == user.newsletter_subscribed
        assert 'referrer_name' in serializer.data
        assert 'approved_by_name' in serializer.data
        assert 'date_joined' in serializer.data
        assert 'updated_at' in serializer.data
        assert 'is_approved_member' in serializer.data
        assert 'full_display_name' in serializer.data 