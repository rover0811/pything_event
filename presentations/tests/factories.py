import factory
from factory.django import DjangoModelFactory

from presentations.models import Presentation, PresentationComment
from users.tests.factories import UserFactory


class PresentationFactory(DjangoModelFactory):
    class Meta:
        model = Presentation

    title = factory.Sequence(lambda n: f"발표 제목 {n}")


class PresentationCommentFactory(DjangoModelFactory):
    class Meta:
        model = PresentationComment

    presentation = factory.SubFactory(PresentationFactory)
    content = factory.Faker('text', max_nb_chars=200, locale='ko_KR')
    guest_name = factory.Faker('name', locale='ko_KR')


class MemberCommentFactory(PresentationCommentFactory):
    """회원 댓글 팩토리"""
    user = factory.SubFactory(UserFactory)
    guest_name = ''  # 회원 댓글은 guest_name 사용 안함


class GuestCommentFactory(PresentationCommentFactory):
    """비회원 댓글 팩토리"""
    user = None
    guest_name = factory.Faker('name', locale='ko_KR')
