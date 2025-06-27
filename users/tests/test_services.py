"""
User 서비스 테스트
Django Styleguide: 서비스는 비즈니스 로직을 담으므로 철저히 테스트
"""
import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from users.services import user_create, user_update, user_approve, user_set_referrer
from users.tests.factories import UserFactory, RegularMemberFactory, AdminUserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserCreateService:
    """user_create 서비스 테스트"""

    def test_user_create_success(self):
        """정상적인 유저 생성"""
        user = user_create(
            email="test@example.com",
            username="김테스트",
            password="testpass123",
            phone="010-1234-5678",
            company="테스트회사"
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "김테스트"
        assert user.phone == "010-1234-5678"
        assert user.company == "테스트회사"
        assert user.user_type == User.UserType.NON_MEMBER
        assert user.check_password("testpass123")

    def test_user_create_with_referrer(self):
        """추천인이 있는 유저 생성"""
        referrer = RegularMemberFactory()

        user = user_create(
            email="test@example.com",
            username="김테스트",
            password="testpass123",
            referrer_id=referrer.id
        )

        assert user.referrer == referrer
        assert user.user_type == User.UserType.ASSOCIATE  # 추천인 있으면 준회원

    def test_user_create_duplicate_email_fails(self):
        """중복 이메일로 유저 생성 실패"""
        UserFactory(email="test@example.com")

        with pytest.raises(ValidationError, match="이미 존재하는 이메일입니다"):
            user_create(
                email="test@example.com",
                username="김테스트",
                password="testpass123"
            )

    def test_user_create_with_non_member_referrer_fails(self):
        """비회원 추천인으로 유저 생성 실패"""
        referrer = UserFactory(user_type=User.UserType.NON_MEMBER)

        with pytest.raises(ValidationError, match="비회원은 추천인이 될 수 없습니다"):
            user_create(
                email="test@example.com",
                username="김테스트",
                password="testpass123",
                referrer_id=referrer.id
            )

    def test_user_create_with_newsletter_subscription(self):
        """뉴스레터 구독 옵션으로 유저 생성"""
        user = user_create(
            email="test@example.com",
            username="김테스트",
            password="testpass123",
            newsletter_subscribed=True
        )

        assert user.newsletter_subscribed is True


@pytest.mark.django_db
class TestUserUpdateService:
    """user_update 서비스 테스트"""

    def test_user_update_success(self):
        """정상적인 유저 정보 업데이트"""
        user = UserFactory()

        updated_user = user_update(
            user=user,
            data={
                'username': '수정된이름',
                'phone': '010-9999-9999',
                'company': '새회사'
            }
        )

        assert updated_user.username == '수정된이름'
        assert updated_user.phone == '010-9999-9999'
        assert updated_user.company == '새회사'

    def test_user_update_partial_data(self):
        """일부 필드만 업데이트"""
        user = UserFactory(username="원래이름", phone="010-1111-1111")

        updated_user = user_update(
            user=user,
            data={'username': '수정된이름'}
        )

        assert updated_user.username == '수정된이름'
        assert updated_user.phone == "010-1111-1111"  # 변경되지 않음

    def test_user_update_empty_data(self):
        """빈 데이터로 업데이트시 변경 없음"""
        user = UserFactory(username="원래이름")
        original_username = user.username

        updated_user = user_update(user=user, data={})

        assert updated_user.username == original_username


@pytest.mark.django_db
class TestUserApproveService:
    """user_approve 서비스 테스트"""

    def test_user_approve_success(self):
        """정상적인 유저 승인"""
        admin = AdminUserFactory()
        user = UserFactory(user_type=User.UserType.ASSOCIATE)

        approved_user = user_approve(user=user, approved_by=admin)

        assert approved_user.user_type == User.UserType.REGULAR
        assert approved_user.approved_by == admin

    def test_user_approve_non_associate_fails(self):
        """준회원이 아닌 유저 승인 실패"""
        admin = AdminUserFactory()
        user = UserFactory(user_type=User.UserType.NON_MEMBER)

        with pytest.raises(ValidationError, match="준회원만 정회원으로 승인 가능합니다"):
            user_approve(user=user, approved_by=admin)

    def test_user_approve_by_non_admin_fails(self):
        """어드민이 아닌 사용자의 승인 실패"""
        regular_user = RegularMemberFactory()
        user = UserFactory(user_type=User.UserType.ASSOCIATE)

        with pytest.raises(ValidationError, match="어드민만 사용자를 승인할 수 있습니다."):
            user_approve(user=user, approved_by=regular_user)

@pytest.mark.django_db
class TestUserSetReferrerService:
    """user_set_referrer 서비스 테스트"""

    def test_set_referrer_success(self):
        """정상적인 추천인 설정"""
        user = UserFactory(user_type=User.UserType.NON_MEMBER)
        referrer = RegularMemberFactory()

        updated_user = user_set_referrer(user=user, referrer=referrer)

        assert updated_user.referrer == referrer
        assert updated_user.user_type == User.UserType.ASSOCIATE  # 준회원 승급

    def test_set_referrer_already_has_referrer_fails(self):
        """이미 추천인이 있는 유저에게 추천인 설정 실패"""
        existing_referrer = RegularMemberFactory()
        user = UserFactory(referrer=existing_referrer)
        new_referrer = RegularMemberFactory()

        with pytest.raises(ValidationError, match="이미 추천인이 설정된 사용자입니다"):
            user_set_referrer(user=user, referrer=new_referrer)

    def test_set_non_member_as_referrer_fails(self):
        """비회원을 추천인으로 설정 실패"""
        user = UserFactory()
        non_member_referrer = UserFactory(user_type=User.UserType.NON_MEMBER)

        with pytest.raises(ValidationError, match="비회원은 추천인이 될 수 없습니다"):
            user_set_referrer(user=user, referrer=non_member_referrer)