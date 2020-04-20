from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.http import HttpResponse
from django.contrib import auth
import factory

from bands.models import (
    City, InstrumentCategory, Instrument, Style,
    Musician, Band,
)
from bands.views import (
    UserDashboardView, ProfileEditView,
)
from users.views import LogInView, LogOutView


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


class TestBandsModels(TestCase):

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
            user.musician.instruments.add(instrument)
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
        assert city_0.name == 'city_0'
        assert city_1.name == 'city_1'
        assert city_0.bands.count() == 1
        assert city_0.musicians.count() == 2

    @staticmethod
    def test_categories_creation():
        category_0 = InstrumentCategory.objects.first()
        category_1 = InstrumentCategory.objects.last()
        assert category_0.name == 'instrument_category_0'
        assert category_0.instruments.count() == 2
        assert category_1.instruments.count() == 2
        assert category_0.instruments.first().name == 'instrument_0'
        assert category_1.instruments.last().name == 'instrument_3'

    @staticmethod
    def test_instruments_creation():
        assert Instrument.objects.count() == 4
        instrument_2 = Instrument.objects.filter(name='instrument_2').first()
        assert instrument_2.category.name == 'instrument_category_1'
        assert instrument_2.musicians.count() == 1
        assert instrument_2.musicians.first().user.username == 'user_2'


class TestDashboard(TestCase):

    DASHBOARD_URL = reverse(UserDashboardView.name)
    LOGIN_URL = reverse(LogInView.name)

    def setUp(self):
        email = 'test@test.ru'
        username = 'test_username'
        password = 'test_password'
        User.objects.create_user(
            email=email,
            username=username,
            password=password,
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_get_dashboard(self):
        login_data = {
            'username': 'test_username',
            'password': 'test_password',
        }
        self.client.post(self.LOGIN_URL, data=login_data)
        response = self.client.get(self.DASHBOARD_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/user_dashboard.html')

    def test_get_dashboard_not_authorized(self):
        response: HttpResponse = self.client.get(self.DASHBOARD_URL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.LOGIN_URL}?next={self.DASHBOARD_URL}')


class TestProfileView(TestCase):

    DASHBOARD_URL = reverse(UserDashboardView.name)
    LOGIN_URL = reverse(LogInView.name)
    LOGOUT_URL = reverse(LogOutView.name)
    PROFILE_EDIT_URL = reverse(ProfileEditView.name)

    def setUp(self):
        email = 'test@test.ru'
        username = 'test_username'
        password = 'test_password'
        User.objects.create_user(
            email=email,
            username=username,
            password=password,
        )
        login_data = {
            'username': 'test_username',
            'password': 'test_password',
        }
        self.client.post(self.LOGIN_URL, data=login_data)

    def tearDown(self):
        User.objects.all().delete()

    def test_get_profile_edit_page(self):
        response: HttpResponse = self.client.get(self.PROFILE_EDIT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/profile_edit.html')

    def test_get_profile_edit_not_authorized(self):
        self.client.get(self.LOGOUT_URL)
        response: HttpResponse = self.client.get(self.PROFILE_EDIT_URL)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.LOGIN_URL}?next={self.PROFILE_EDIT_URL}')

    def test_post_profile_edit_name_date(self):
        profile_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'birth_date': '1988-04-17',
        }
        response: HttpResponse = self.client.post(self.PROFILE_EDIT_URL, data=profile_data)
        self.assertTrue(response.status_code, 302)
        self.assertRedirects(response, self.DASHBOARD_URL)
        user: User = auth.get_user(self.client)
        musician = Musician.objects.filter(user=user).first()
        self.assertEqual(musician.first_name, 'John')
        self.assertEqual(musician.last_name, 'Doe')
        self.assertEqual(musician.birth_date, '1988-04-17')

    def test_post_profile_edit_relations(self):
        pass
