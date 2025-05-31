# locations/tests/factories.py
import factory
from factory.django import DjangoModelFactory

from locations.models import Location


class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location

    name = factory.Sequence(lambda n: f"테스트장소{n}")
    address = factory.Faker('address', locale='ko_KR')
    description = factory.Faker('text', max_nb_chars=200, locale='ko_KR')
    max_capacity = factory.Faker('random_int', min=10, max=300)


class SmallLocationFactory(LocationFactory):
    """소규모 장소 (10-50명)"""
    max_capacity = factory.Faker('random_int', min=10, max=50)


class LargeLocationFactory(LocationFactory):
    """대규모 장소 (100-300명)"""
    max_capacity = factory.Faker('random_int', min=100, max=300)