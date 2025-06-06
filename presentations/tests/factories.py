import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory.django import DjangoModelFactory

from presentations.models import Presentation, PresentationComment


def get_user_factory():
    from users.tests.factories import UserFactory
    return UserFactory


def get_regular_member_factory():
    from users.tests.factories import RegularMemberFactory
    return RegularMemberFactory


def get_event_factory():
    from events.tests.factories import EventFactory
    return EventFactory


class PresentationFactory(DjangoModelFactory):
    class Meta:
        model = Presentation

    title = factory.Sequence(lambda n: f"발표 제목 {n}")
    description = factory.Faker('text', max_nb_chars=200, locale='ko_KR')
    content_md = factory.Faker('text', max_nb_chars=5000, locale='ko_KR')
    presenter = factory.SubFactory(get_regular_member_factory())
    event = factory.SubFactory(get_event_factory())


class PresentationWithFileFactory(PresentationFactory):
    """파일이 포함된 발표 팩토리"""

    @factory.post_generation
    def file_url(self, create, extracted, **kwargs):
        if not create:
            return

        file_content = b"PDF test content " * 1000
        uploaded_file = SimpleUploadedFile(
            "test_presentation.pdf",
            file_content,
            content_type="application/pdf"
        )
        self.file_url.save(uploaded_file.name, uploaded_file, save=True)

class SelectedPresentationFactory(PresentationFactory):
    """선정된 발표 팩토리"""
    status = Presentation.Status.SELECTED
    selected_for_newsletter = True


class CompletedPresentationFactory(PresentationFactory):
    """완료된 발표 팩토리"""
    status = Presentation.Status.COMPLETED


class RejectedPresentationFactory(PresentationFactory):
    """거절된 발표 팩토리"""
    status = Presentation.Status.REJECTED


class PresentationCommentFactory(DjangoModelFactory):
    class Meta:
        model = PresentationComment

    presentation = factory.SubFactory(PresentationFactory)
    content = factory.Faker('text', max_nb_chars=200, locale='ko_KR')
    guest_name = factory.Faker('name', locale='ko_KR')


class MemberCommentFactory(PresentationCommentFactory):
    """회원 댓글 팩토리"""
    user = factory.SubFactory(get_user_factory())
    guest_name = ''  # 회원 댓글은 guest_name 사용 안함


class GuestCommentFactory(PresentationCommentFactory):
    """비회원 댓글 팩토리"""
    user = None
    guest_name = None
