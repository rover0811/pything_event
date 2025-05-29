# users/tests/factories.py - 임시로 간단화
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.LazyAttribute(lambda obj: obj.email)
    name = factory.Faker('name')
    user_type = User.UserType.NON_MEMBER
    newsletter_subscribed = False
    is_active = True

    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        if not create:
            return
        self.set_password('testpass123')


class AdminUserFactory(UserFactory):
    user_type = User.UserType.ADMIN
    is_staff = True
    is_superuser = True


class AssociateMemberFactory(UserFactory):
    user_type = User.UserType.ASSOCIATE