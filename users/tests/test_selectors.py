"""
User 셀렉터 테스트
"""
import pytest
from django.contrib.auth import get_user_model

from users.selectors import (
    user_list, user_get, user_get_by_email,
    user_get_pending_approval
)
from users.tests.factories import (
    UserFactory, RegularMemberFactory,
    AssociateMemberFactory, UserWithReferrerFactory
)

User = get_user_model()


@pytest.mark.django_db
class TestUserListSelector:
    """user_list 셀렉터 테스트"""

    def test_user_list_returns_all_users(self):
        """모든 유저 목록 반환"""
        UserFactory.create_batch(3)

        users = user_list()

        assert users.count() == 3

    def test_user_list_filter_by_user_type(self):
        """user_type 필터링"""
        UserFactory.create_batch(2, user_type=User.UserType.NON_MEMBER)
        RegularMemberFactory.create_batch(3)

        regular_users = user_list(filters={'user_type': User.UserType.REGULAR})

        assert regular_users.count() == 3

    def test_user_list_filter_by_newsletter_subscription(self):
        """뉴스레터 구독 필터링"""
        UserFactory.create_batch(2, newsletter_subscribed=True)
        UserFactory.create_batch(3, newsletter_subscribed=False)

        subscribed_users = user_list(filters={'newsletter_subscribed': True})

        assert subscribed_users.count() == 2

    def test_user_list_search_by_name(self):
        """이름으로 검색"""
        UserFactory(name="김철수")
        UserFactory(name="이영희")
        UserFactory(name="박철수")

        search_results = user_list(filters={'search': '철수'})

        assert search_results.count() == 2

    def test_user_list_filter_has_referrer(self):
        """추천인 유무 필터링"""
        UserWithReferrerFactory.create_batch(2)
        UserFactory.create_batch(3)  # 추천인 없음

        users_with_referrer = user_list(filters={'has_referrer': True})
        users_without_referrer = user_list(filters={'has_referrer': False})

        assert users_with_referrer.count() == 2
        assert users_without_referrer.count() == 3


@pytest.mark.django_db
class TestUserGetSelectors:
    """user_get 관련 셀렉터 테스트"""

    def test_user_get_by_id(self):
        """ID로 유저 조회"""
        user = UserFactory()

        found_user = user_get(user_id=user.id)

        assert found_user == user

    def test_user_get_by_email(self):
        """이메일로 유저 조회"""
        user = UserFactory(email="test@example.com")

        found_user = user_get_by_email(email="test@example.com")

        assert found_user == user

    def test_user_get_nonexistent_raises_exception(self):
        """존재하지 않는 유저 조회시 예외 발생"""
        with pytest.raises(User.DoesNotExist):
            user_get(user_id=99999)


@pytest.mark.django_db
class TestUserGetPendingApproval:
    """user_get_pending_approval 셀렉터 테스트"""

    def test_get_pending_approval_users(self):
        """승인 대기 유저 목록 조회"""
        # 승인 대기 (approved_by가 None)
        AssociateMemberFactory.create_batch(3, approved_by=None)

        # 이미 승인된 유저
        admin = UserFactory(user_type=User.UserType.ADMIN)
        AssociateMemberFactory(approved_by=admin)

        # 비회원, 정회원 (승인 대상 아님)
        UserFactory(user_type=User.UserType.NON_MEMBER)
        RegularMemberFactory()

        pending_users = user_get_pending_approval()

        assert pending_users.count() == 3
        for user in pending_users:
            assert user.user_type == User.UserType.ASSOCIATE
            assert user.approved_by is None
