import pytest
from presentations.serializers import PresentationCommentSerializer
from presentations.tests.factories import PresentationFactory
from users.tests.factories import UserFactory
from rest_framework.test import APIRequestFactory


@pytest.mark.django_db
class TestPresentationCommentSerializer:
    """PresentationComment Serializer 테스트"""

    def test_guest_comment_serialization(self):
        """비회원 댓글 직렬화 테스트"""
        from presentations.tests.factories import GuestCommentFactory

        comment = GuestCommentFactory(
            content="테스트 댓글"
        )

        serializer = PresentationCommentSerializer(comment)
        data = serializer.data

        assert data['author_name'] == "Anonymous"
        assert data['content'] == "테스트 댓글"
        assert data['user'] is None

    def test_member_comment_serialization(self):
        """회원 댓글 직렬화 테스트"""
        from presentations.tests.factories import MemberCommentFactory

        user = UserFactory(username="김개발")
        comment = MemberCommentFactory(user=user, content="회원 댓글")

        serializer = PresentationCommentSerializer(comment)
        data = serializer.data

        assert data['author_name'] == "김개발"
        assert data['content'] == "회원 댓글"
        assert data['user'] == user.id

    def test_create_guest_comment(self):
        """비회원 댓글 생성 테스트"""
        presentation = PresentationFactory()

        # 비인증 요청 시뮬레이션
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = type('AnonymousUser', (), {'is_authenticated': False})()

        data = {
            'presentation': presentation.id,
            'content': '비회원 댓글',
        }

        serializer = PresentationCommentSerializer(
            data=data,
            context={'request': request}
        )

        assert serializer.is_valid()
        comment = serializer.save()

        assert comment.content == '비회원 댓글'
        assert comment.guest_name == 'Anonymous'
        assert comment.user is None

    def test_create_member_comment(self):
        """회원 댓글 생성 테스트"""
        user = UserFactory(username="김개발")
        presentation = PresentationFactory()

        # 인증된 요청 시뮬레이션
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = user

        data = {
            'presentation': presentation.id,
            'content': '회원 댓글'
        }

        serializer = PresentationCommentSerializer(
            data=data,
            context={'request': request}
        )

        assert serializer.is_valid()
        comment = serializer.save()

        assert comment.content == '회원 댓글'
        assert comment.user == user
        assert comment.author_name == "김개발"
