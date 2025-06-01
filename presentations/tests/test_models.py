import pytest
from presentations.tests.factories import (
    PresentationCommentFactory,
    MemberCommentFactory,
    GuestCommentFactory
)
from users.tests.factories import UserFactory


@pytest.mark.django_db
class TestPresentationCommentModel:
    """PresentationComment 모델 테스트"""

    def test_guest_comment_author_name(self):
        """비회원 댓글의 author_name은 guest_name"""
        comment = GuestCommentFactory(guest_name="익명사용자")

        assert comment.author_name == "익명사용자"
        assert comment.user is None

    def test_member_comment_author_name(self):
        """회원 댓글의 author_name은 user.name"""
        user = UserFactory(name="김개발")
        comment = MemberCommentFactory(user=user)

        assert comment.author_name == "김개발"
        assert comment.user == user

    def test_default_guest_name(self):
        """guest_name 기본값은 Anonymous"""
        comment = PresentationCommentFactory(guest_name="")

        # 모델의 default 값 확인
        assert comment._meta.get_field('guest_name').default == 'Anonymous'

    def test_str_representation(self):
        """__str__ 메서드 테스트"""
        comment = GuestCommentFactory(
            guest_name="테스터",
            content="이것은 테스트 댓글입니다. 긴 내용을 가지고 있어서 50자를 넘어갑니다"
        )

        expected = "테스터: 이것은 테스트 댓글입니다. 긴 내용을 가지고 있어서 50자를 넘어갑니다"
        assert str(comment) == expected
