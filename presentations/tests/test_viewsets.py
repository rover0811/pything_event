import pytest
from django.urls import reverse
from rest_framework import status

from presentations.tests.factories import (
    PresentationFactory,
    PresentationCommentFactory,
    MemberCommentFactory,
    GuestCommentFactory
)
from users.tests.factories import UserFactory


@pytest.mark.django_db
class TestPresentationCommentViewSet:
    """PresentationComment ViewSet 테스트"""

    def test_list_comments(self, api_client):
        """댓글 목록 조회"""
        PresentationCommentFactory.create_batch(3)

        url = reverse('presentation-comments-list')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_guest_create_comment_with_name(self, api_client):
        """비회원 댓글 생성 (이름 포함)"""
        presentation = PresentationFactory()

        url = reverse('presentation-comments-list')
        data = {
            'presentation': presentation.id,
            'content': '비회원 댓글입니다',
            'guest_name': 'Anonymous'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == '비회원 댓글입니다'
        assert response.data['author_name'] == 'Anonymous'
        assert response.data['user'] is None

    def test_guest_create_comment_without_name(self, api_client):
        """비회원 댓글 생성 (이름 없음 - Anonymous 기본값)"""
        presentation = PresentationFactory()

        url = reverse('presentation-comments-list')
        data = {
            'presentation': presentation.id,
            'content': '익명 댓글입니다'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == '익명 댓글입니다'
        assert response.data['author_name'] == 'Anonymous'
        assert response.data['user'] is None

    def test_member_create_comment(self, api_client):
        """회원 댓글 생성"""
        user = UserFactory(username="김개발")
        api_client.force_authenticate(user=user)
        presentation = PresentationFactory()

        url = reverse('presentation-comments-list')
        data = {
            'presentation': presentation.id,
            'content': '회원 댓글입니다'
        }

        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['content'] == '회원 댓글입니다'
        assert response.data['author_name'] == '김개발'
        assert response.data['user'] == user.id

    def test_retrieve_comment(self, api_client):
        """댓글 상세 조회"""
        comment = GuestCommentFactory(
            guest_name="테스터",
            content="상세 조회 테스트"
        )

        url = reverse('presentation-comments-detail', kwargs={'pk': comment.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == comment.id
        assert response.data['content'] == "상세 조회 테스트"
        assert response.data['author_name'] == "테스터"

    def test_update_member_comment_success(self, api_client):
        """회원 댓글 수정 성공 (본인)"""
        user = UserFactory()
        api_client.force_authenticate(user=user)
        comment = MemberCommentFactory(user=user, content="원본 댓글")

        url = reverse('presentation-comments-detail', kwargs={'pk': comment.id})
        data = {'content': '수정된 댓글'}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['content'] == '수정된 댓글'

    def test_update_member_comment_forbidden(self, api_client):
        """회원 댓글 수정 실패 (다른 사용자)"""
        user1 = UserFactory()
        user2 = UserFactory()
        api_client.force_authenticate(user=user2)
        comment = MemberCommentFactory(user=user1)

        url = reverse('presentation-comments-detail', kwargs={'pk': comment.id})
        data = {'content': '수정 시도'}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_guest_comment_forbidden(self, api_client):
        """비회원 댓글 수정 실패"""
        user = UserFactory()
        api_client.force_authenticate(user=user)
        comment = GuestCommentFactory()

        url = reverse('presentation-comments-detail', kwargs={'pk': comment.id})
        data = {'content': '수정 시도'}

        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_member_comment_success(self, api_client):
        """회원 댓글 삭제 성공 (본인)"""
        user = UserFactory()
        api_client.force_authenticate(user=user)
        comment = MemberCommentFactory(user=user)
        comment_id = comment.id

        url = reverse('presentation-comments-detail', kwargs={'pk': comment.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 댓글이 삭제되었는지 확인
        from presentations.models import PresentationComment
        assert not PresentationComment.objects.filter(id=comment_id).exists()

    def test_delete_guest_comment_forbidden(self, api_client):
        """비회원 댓글 삭제 실패"""
        user = UserFactory()
        api_client.force_authenticate(user=user)
        comment = GuestCommentFactory()

        url = reverse('presentation-comments-detail', kwargs={'pk': comment.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_access_allowed(self, api_client):
        """비인증 사용자도 목록/상세 조회 가능"""
        comment = GuestCommentFactory()

        # 목록 조회
        list_url = reverse('presentation-comments-list')
        list_response = api_client.get(list_url)
        assert list_response.status_code == status.HTTP_200_OK

        # 상세 조회
        detail_url = reverse('presentation-comments-detail', kwargs={'pk': comment.id})
        detail_response = api_client.get(detail_url)
        assert detail_response.status_code == status.HTTP_200_OK
