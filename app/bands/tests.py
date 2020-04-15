from django.test import TestCase
from django.contrib.auth.models import User
import factory

from bands.models import (
    City, InstrumentCategory, Instrument, Style,
    Musician, Band,
)


class CityFactory(factory.DjangoModelFactory):

    class Meta:
        model = City

    name = factory.Sequence(lambda n: f'city_{n}')


class InstrumentCategoryFactory(factory.DjangoModelFactory):

    class Meta:
        model = InstrumentCategory

    name = factory.Sequence(lambda n: f'instrument_category_{n}')


class InstrumentFactory(factory.DjangoModelFactory):

    class Meta:
        model = Instrument

    name = factory.Sequence(lambda n: f'instrument_{n}')
    category = factory.SubFactory(InstrumentCategoryFactory)


class StyleFactory(factory.DjangoModelFactory):

    class Meta:
        model = Style

    name = factory.Sequence(lambda n: f'style_{n}')


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user_{n}')
    password = factory.Sequence(lambda n: f'password_{n}')


class BandFactory(factory.DjangoModelFactory):

    class Meta:
        model = Band

    name = factory.Sequence(lambda n: f'band_{n}')

    @factory.post_generation
    def styles(self, created, extracted, **kwargs):
        if not created:
            return None
        if extracted:
            for style in extracted:
                self.styles.add(style)


class TestBands(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Creating objects:
            City — 2
            InstrumentCategories — 2
            Instruments — 4 overall: 2 for each category
            Styles — 2
            Users(Musicians) — 4 overall: 2 for each City and Band,
                each has unique instrument
            Bands — 2 overall: each has unique City and Style
        """
        cities = CityFactory.create_batch(size=2)
        instrument_categories = InstrumentCategoryFactory.create_batch(size=2)
        instruments = [InstrumentFactory.create_batch(size=2, category=category)
                       for category in instrument_categories]
        instruments = [instrument for instrument_group in instruments
                       for instrument in instrument_group]
        styles = StyleFactory.create_batch(size=2)
        users = UserFactory.create_batch(size=4)
        bands = [BandFactory.create(styles=(styles[n], ), city=cities[n])
                 for n in range(2)]
        for user in users[:2]:
            user.musician.bands.add(bands[0])
            user.musician.city = cities[0]
            user.save()

        for user in users[2:]:
            user.musician.bands.add(bands[1])
            user.musician.city = cities[1]
            user.save()

        for user, instrument in zip(users, instruments):
            user.musician.instrument = instrument
            user.save()

    @classmethod
    def tearDownClass(cls):
        pass

    @staticmethod
    def test_representation():
        assert City.objects.first().__str__() == '<City: city_0>'
        assert Instrument.objects.last().__str__() == '<Instrument: instrument_3>'
        musician = Musician.objects.filter(user__username='user_0').first()
        musician.first_name = 'John'
        musician.last_name = 'Doe'
        assert musician.__str__() == '<Musician: John username: user_0 Doe>'
        assert Band.objects.first().__str__() == '<Band: band_0 id: 1>'
        assert Style.objects.last().__str__() == '<Style: style_1>'
        category = InstrumentCategory.objects.last()
        assert category.__str__() == '<InstrumentCategory: instrument_category_1>'

    @staticmethod
    def test_city_creation():
        city_0 = City.objects.first()
        city_1 = City.objects.last()
        assert City.objects.count() == 2
        assert city_1.name == 'city_1'
        assert city_0.bands.count() == 1
        assert city_0.musicians.count() == 2

    @staticmethod
    def test_categories_creation():
        category_0 = InstrumentCategory.objects.first()
        assert category_0.name == 'instrument_category_0'
        assert category_0.instruments.count() == 2
        assert category_0.instruments.first().name == 'instrument_0'
