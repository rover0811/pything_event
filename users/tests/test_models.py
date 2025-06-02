"""
User 모델 테스트
Django Styleguide: 모델은 검증, 속성, 메서드가 있을 때만 테스트
"""
import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from users.tests.factories import UserFactory, RegularMemberFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """User 모델 테스트"""

    def test_user_creation_with_factory(self):
        """팩토리로 유저 생성 테스트"""
        user = UserFactory()

        assert user.id is not None
        assert user.email
        assert user.name
        assert user.user_type == User.UserType.NON_MEMBER
        assert not user.newsletter_subscribed

    def test_user_string_representation(self):
        """__str__ 메서드 테스트"""
        user = UserFactory(name="김테스트", email="test@example.com")

        expected = "김테스트 (test@example.com)"
        assert str(user) == expected

    def test_user_full_display_name_property(self):
        """full_display_name 속성 테스트"""
        user = UserFactory(name="김테스트", email="test@example.com")

        expected = "김테스트 (test@example.com)"
        assert user.full_display_name == expected

    def test_is_approved_member_property_for_regular_member(self):
        """정회원의 is_approved_member 속성 테스트"""
        user = UserFactory(user_type=User.UserType.REGULAR)

        assert user.is_approved_member is True

    def test_is_approved_member_property_for_non_member(self):
        """비회원의 is_approved_member 속성 테스트"""
        user = UserFactory(user_type=User.UserType.NON_MEMBER)

        assert user.is_approved_member is False

    def test_clean_method_prevents_self_referral(self):
        """clean() 메서드 - 자기 자신 추천인 설정 방지"""
        user = UserFactory.build()  # DB에 저장하지 않음
        user.referrer = user

        with pytest.raises(ValidationError, match="자기 자신을 추천인으로 설정할 수 없습니다"):
            user.full_clean()

    def test_clean_method_prevents_self_approval(self):
        """clean() 메서드 - 자기 자신 승인자 설정 방지"""
        user = UserFactory.build()
        user.approved_by = user

        with pytest.raises(ValidationError, match="자기 자신을 승인자로 설정할 수 없습니다"):
            user.full_clean()

    def test_clean_method_allows_valid_referrer(self):
        """clean() 메서드 - 유효한 추천인은 허용"""
        referrer = RegularMemberFactory()
        user = UserFactory.build(referrer=referrer)

        # password 설정 (AbstractUser 상속으로 인한 필수 필드)
        user.set_password('testpass123')

        # 예외 발생하지 않아야 함
        user.full_clean()
        assert user.referrer == referrer

    def test_username_field_is_email(self):
        """USERNAME_FIELD가 email인지 확인"""
        assert User.USERNAME_FIELD == 'email'

    def test_required_fields_contains_name(self):
        """REQUIRED_FIELDS에 name이 포함되는지 확인"""
        assert 'name' in User.REQUIRED_FIELDS