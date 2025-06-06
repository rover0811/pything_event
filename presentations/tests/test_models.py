import pytest
from django.core.exceptions import ValidationError
from presentations.tests.factories import PresentationFactory
from users.tests.factories import UserFactory
from presentations.models import PresentationComment


@pytest.mark.django_db
class TestPresentationCommentModel:
    """PresentationComment 모델 테스트"""

    def test_member_comment_clears_guest_name(self):
        """회원 댓글 생성 시 guest_name이 자동으로 비워짐"""
        user = UserFactory(name="김개발")
        presentation = PresentationFactory()

        comment = PresentationComment(
            presentation=presentation,
            content="회원 댓글",
            user=user,
            guest_name="이것은 무시됨"  # 이 값은 clean()에서 비워짐
        )
        comment.save()

        assert comment.guest_name == ""
        assert comment.author_name == "김개발"
        assert comment.is_member_comment is True

    def test_guest_name_becomes_anonymous_after_clean(self):
        """비회원 댓글에서 guest_name이 비어있으면 clean() 후 Anonymous가 됨"""
        presentation = PresentationFactory()

        comment = PresentationComment(
            presentation=presentation,
            content="비회원 댓글",
            user=None,
            guest_name=""  # 비어있음
        )

        # clean() 호출 전에는 빈 문자열
        assert comment.guest_name == ""

        # clean() 호출 후 Anonymous로 변경
        comment.clean()
        assert comment.guest_name == "Anonymous"

        # save() 시에도 동일 (save에서 full_clean 호출하므로)
        comment.save()
        assert comment.guest_name == "Anonymous"

    def test_member_comment_edit_permission(self):
        """회원 댓글 수정 권한 테스트"""
        user = UserFactory()
        other_user = UserFactory()
        presentation = PresentationFactory()

        comment = PresentationComment.objects.create(
            presentation=presentation,
            content="회원 댓글",
            user=user
        )

        # 본인은 수정 가능
        assert comment.can_edit(user) is True
        # 다른 사용자는 수정 불가
        assert comment.can_edit(other_user) is False
        # 비인증 사용자는 수정 불가
        assert comment.can_edit(None) is False

    def test_guest_comment_edit_permission(self):
        """비회원 댓글 수정 권한 테스트 (수정 불가)"""
        user = UserFactory()
        presentation = PresentationFactory()

        comment = PresentationComment.objects.create(
            presentation=presentation,
            content="비회원 댓글",
            guest_name="익명"
        )

        # 비회원 댓글은 누구도 수정 불가
        assert comment.can_edit(user) is False
        assert comment.can_edit(None) is False

    def test_admin_can_delete_all_comments(self):
        """어드민은 모든 댓글 삭제 가능"""
        from users.models import User

        admin = UserFactory(user_type=User.UserType.ADMIN)
        regular_user = UserFactory()
        presentation = PresentationFactory()

        # 회원 댓글
        member_comment = PresentationComment.objects.create(
            presentation=presentation,
            content="회원 댓글",
            user=regular_user
        )

        # 비회원 댓글
        guest_comment = PresentationComment.objects.create(
            presentation=presentation,
            content="비회원 댓글",
            guest_name="익명"
        )

        # 어드민은 모든 댓글 삭제 가능
        assert member_comment.can_delete(admin) is True
        assert guest_comment.can_delete(admin) is True

    def test_str_representation(self):
        """문자열 표현 테스트"""
        user = UserFactory(name="김개발")
        presentation = PresentationFactory()

        # 회원 댓글
        member_comment = PresentationComment.objects.create(
            presentation=presentation,
            content="이것은 긴 댓글 내용입니다. 50자를 넘어가는 내용입니다.",
            user=user
        )

        # 비회원 댓글
        guest_comment = PresentationComment.objects.create(
            presentation=presentation,
            content="비회원 댓글입니다.",
            guest_name="익명사용자"
        )

        assert str(member_comment).startswith("[회원] 김개발:")
        assert str(guest_comment).startswith("[비회원] 익명사용자:")