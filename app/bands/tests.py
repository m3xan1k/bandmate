from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from django.http import HttpResponse, HttpRequest
from django.contrib import auth
from django.db.models.query import QuerySet
import factory

from bands.models import (
    City, InstrumentCategory, Instrument, Style,
    Musician, Band,
)
from bands.views import (
    UserDashboardView, ProfileEditView, MusiciansView, BandsDashboardView,
    BandEditView, BandsView,
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
        bands = [BandFactory.create(styles=(styles[n], ), city=cities[n], admin=users[n + 1])
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

        for user in users[:2]:
            user.musician.activated = True
            user.musician.save()

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        City.objects.all().delete()
        Instrument.objects.all().delete()
        InstrumentCategory.objects.all().delete()
        Musician.objects.all().delete()
        Band.objects.all().delete()
        Style.objects.all().delete()
        StyleFactory.reset_sequence()
        UserFactory.reset_sequence()
        BandFactory.reset_sequence()
        CityFactory.reset_sequence()
        StyleFactory.reset_sequence()
        UserFactory.reset_sequence()
        InstrumentFactory.reset_sequence()
        InstrumentCategoryFactory.reset_sequence()

    @staticmethod
    def test_stringify():
        assert City.objects.first().__str__() == 'city_0'
        assert Instrument.objects.last().__str__() == 'instrument_3'
        musician = Musician.objects.filter(user__username='user_0').first()
        musician.first_name = 'John'
        musician.last_name = 'Doe'
        assert musician.__str__() == 'John user_0 Doe'
        assert Band.objects.first().__str__() == 'band_0'
        assert Style.objects.last().__str__() == 'style_1'
        category = InstrumentCategory.objects.last()
        assert category.__str__() == 'instrument_category_1'

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

    def test_musicians_creation(self):
        self.assertEqual(Musician.objects.count(), 4)
        self.assertEqual(Musician.activated_objects.count(), 2)
        musician_0 = Musician.objects.filter(user__username='user_0').first()
        self.assertEqual(musician_0.bands.count(), 1)
        self.assertEqual(musician_0.bands.first().name, 'band_0')
        self.assertEqual(musician_0.instruments.count(), 1)
        self.assertEqual(musician_0.instruments.first().name, 'instrument_0')

    def test_styles_creation(self):
        self.assertEqual(Style.objects.count(), 2)
        style_0 = Style.objects.filter(name='style_0').first()
        self.assertEqual(style_0.bands.count(), 1)
        self.assertEqual(style_0.bands.first().name, 'band_0')

    def test_bands_creation(self):
        self.assertEqual(Band.objects.count(), 2)
        band_1 = Band.objects.filter(name='band_1').first()
        self.assertEqual(band_1.admin.username, 'user_2')
        self.assertEqual(band_1.musicians.count(), 2)
        self.assertEqual(band_1.musicians.first().user.username, 'user_2')
        self.assertEqual(band_1.styles.first().name, 'style_1')
        band_0 = Band.objects.filter(name='band_0').first()
        self.assertEqual(band_0.admin.username, 'user_1')


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
        self.assertEqual(musician.birth_date.strftime('%Y-%m-%d'), '1988-04-17')

    def test_post_profile_edit_relations(self):
        city = City.objects.create(name='Moscow')
        instrument = Instrument.objects.create(name='Guitar')
        profile_data = {
            'city': city.id,
            'instruments': (instrument.id, ),
        }
        response: HttpResponse = self.client.post(self.PROFILE_EDIT_URL, data=profile_data)
        self.assertTrue(response.status_code, 302)
        self.assertRedirects(response, self.DASHBOARD_URL)

        user: User = auth.get_user(self.client)
        self.assertEqual(user.musician.city.name, 'Moscow')
        self.assertEqual(user.musician.instruments.count(), 1)
        self.assertEqual(user.musician.instruments.all()[0].name, 'Guitar')


class TestMusiciansViews(TestCase):

    MUSICIANS_URL = reverse(MusiciansView.name)

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
        bands = [BandFactory.create(styles=(styles[n], ), city=cities[n], admin=users[n + 1])
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

        for user in users:
            user.musician.activated = True
            user.musician.save()

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        City.objects.all().delete()
        Instrument.objects.all().delete()
        InstrumentCategory.objects.all().delete()
        Musician.objects.all().delete()
        Band.objects.all().delete()
        Style.objects.all().delete()
        StyleFactory.reset_sequence()
        UserFactory.reset_sequence()
        BandFactory.reset_sequence()
        CityFactory.reset_sequence()
        StyleFactory.reset_sequence()
        UserFactory.reset_sequence()
        InstrumentFactory.reset_sequence()
        InstrumentCategoryFactory.reset_sequence()

    def setUp(self):
        # to reset django cache
        request = HttpRequest()
        musicians_view = MusiciansView()
        musicians_view.get(request)

    def test_musicians_view(self):
        response: HttpResponse = self.client.get(self.MUSICIANS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/musicians.html')
        self.assertEqual(len(response.context[0].get('musicians')), 4)

    def test_musician_detail_view(self):
        musician = Musician.objects.first()
        response: HttpResponse = self.client.get(f'{self.MUSICIANS_URL}{musician.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/musician.html')

    def test_musicians_view_filter_instrument(self):
        instrument = Instrument.objects.last()
        response = self.client.get(
            f'{self.MUSICIANS_URL}?instrument={instrument.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/musicians.html')
        self.assertEqual(len(response.context[0].get('musicians')), 1)

    def test_musicians_view_filter_city(self):
        city = City.objects.first()
        response = self.client.get(f'{self.MUSICIANS_URL}?city={city.id}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/musicians.html')
        self.assertEqual(len(response.context[0].get('musicians')), 2)

    def test_musicians_view_filter_combined_empty(self):
        instrument = Instrument.objects.first()
        city = City.objects.last()
        response = self.client.get(
            f'{self.MUSICIANS_URL}?instrument={instrument.id}&city={city.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/musicians.html')
        self.assertEqual(len(response.context[0].get('musicians')), 0)

    def test_musicians_view_filter_combined(self):
        instrument = Instrument.objects.first()
        city = City.objects.first()
        response = self.client.get(
            f'{self.MUSICIANS_URL}?instrument={instrument.id}&city={city.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/musicians.html')
        self.assertEqual(len(response.context[0].get('musicians')), 1)

    def test_musicians_order_by_busy(self):
        # setup
        musicians = Musician.objects.all()
        for musician in musicians[:2]:
            musician.is_busy = True
            musician.save()

        response: HttpResponse = self.client.get(self.MUSICIANS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/musicians.html')
        musicians = response.context[0].get('musicians').object_list
        self.assertEqual(len(musicians), 4)
        for musician in musicians[:2]:
            self.assertFalse(musician.is_busy)
        for musician in musicians[2:]:
            self.assertTrue(musician.is_busy)


class TestBandAdminViews(TestCase):

    MUSICIANS_URL = reverse(MusiciansView.name)
    BANDS_DASHBOARD_URL = reverse(BandsDashboardView.name)
    BAND_EDIT_URL = reverse(BandEditView.name)
    LOGIN_URL = reverse(LogInView.name)
    LOGOUT_URL = reverse(LogOutView.name)

    @classmethod
    def setUpClass(cls):
        """
        Creating objects:
            City — 2
            Styles — 2
            Users(Musicians) — 4 overall: 2 for each Band
            Bands — 2 overall: each has unique City and Style
            user_1 is admin for band_0
            user_2 is admin for band_1
        """
        StyleFactory.reset_sequence()
        UserFactory.reset_sequence()
        BandFactory.reset_sequence()
        CityFactory.reset_sequence()
        users = UserFactory.create_batch(size=4)
        styles = StyleFactory.create_batch(size=2)
        cities = CityFactory.create_batch(size=2)
        [BandFactory.create(styles=(styles[n], ), city=cities[n], admin=users[n + 1])
         for n in range(2)]

        for user in users:
            user.musician.activated = True
            user.musician.save()

        for user in users:
            user.set_password(user.password)
            user.save()

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        City.objects.all().delete()
        Musician.objects.all().delete()
        Band.objects.all().delete()
        Style.objects.all().delete()
        StyleFactory.reset_sequence()
        UserFactory.reset_sequence()
        BandFactory.reset_sequence()
        CityFactory.reset_sequence()
        StyleFactory.reset_sequence()
        UserFactory.reset_sequence()
        InstrumentFactory.reset_sequence()
        InstrumentCategoryFactory.reset_sequence()

    def setUp(self):
        # to reset django cache
        # request = HttpRequest()
        # dashboard_view = BandsDashboardView()
        # dashboard_view.get(request)

        login_data = {
            'username': 'user_1',
            'password': 'password_1',
        }
        self.client.post(self.LOGIN_URL, data=login_data)

    def tearDown(self):
        self.client.get(self.LOGOUT_URL)

    def test_bands_dashboard(self):
        response: HttpResponse = self.client.get(self.BANDS_DASHBOARD_URL)
        user: User = auth.get_user(self.client)
        self.assertTemplateUsed(response, 'bands/bands_dashboard.html')

        bands: QuerySet = response.context[0].get('bands')
        self.assertEqual(bands.count(), 1)
        self.assertEqual(bands[0].name, 'band_0')
        self.assertEqual(user, bands[0].admin)

    def test_bands_dashboard_not_authorized(self):
        self.client.get(self.LOGOUT_URL)
        response: HttpResponse = self.client.get(self.BANDS_DASHBOARD_URL)
        self.assertRedirects(response, F'{self.LOGIN_URL}?next={self.BANDS_DASHBOARD_URL}')

    def test_band_edit_page_get(self):
        response: HttpResponse = self.client.get(self.BAND_EDIT_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/band_edit.html')

        band_0 = Band.objects.filter(name='band_0').first()
        response: HttpResponse = self.client.get(f'{self.BAND_EDIT_URL}{band_0.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/band_edit.html')

        response: HttpResponse = self.client.get(f'{self.BAND_EDIT_URL}{band_0.id + 1}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')

        response: HttpResponse = self.client.get(f'{self.BAND_EDIT_URL}{band_0.id + 2}/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_band_creation(self):
        user_1 = auth.get_user(self.client)
        user_3 = User.objects.filter(username='user_3').first()
        city = City.objects.create(name='new_city')
        new_band_data = {
            'name': 'new_band',
            'musicians': [user_1.id, user_3.id],
            'city': city.id,
            'description': 'Hello',
        }
        response: HttpResponse = self.client.post(self.BAND_EDIT_URL, new_band_data)
        self.assertRedirects(response, self.BANDS_DASHBOARD_URL)

        new_band = Band.objects.filter(name='new_band').first()
        self.assertEqual(new_band.admin, user_1)
        self.assertEqual(new_band.city, city)
        self.assertEqual(new_band.description, 'Hello')
        self.assertEqual(
            new_band.musicians.order_by('id').all()[0],
            Musician.objects.filter(id__in=[user_1.id, user_3.id]).order_by('id').all()[0])
        self.assertEqual(
            new_band.musicians.order_by('id').all()[1],
            Musician.objects.filter(id__in=[user_1.id, user_3.id]).order_by('id').all()[1])

        response: HttpResponse = self.client.get(self.BANDS_DASHBOARD_URL)

        bands: QuerySet = response.context[0].get('bands')
        self.assertEqual(bands.count(), 2)
        self.assertEqual(bands[1].name, 'new_band')

    def test_band_put(self):
        band_0 = Band.objects.filter(name='band_0').first()
        band_data = {
            'name': 'band_0_edited',
            'musicians': [auth.get_user(self.client).id],
            'description': 'edited',
        }

        header = {'HTTP_X_HTTP_METHOD_OVERRIDE': 'PUT'}
        response: HttpResponse = self.client.post(f'{self.BAND_EDIT_URL}{band_0.id}/',
                                                  data=band_data,
                                                  **header)
        self.assertRedirects(response, self.BANDS_DASHBOARD_URL)

        band_0_edited = Band.objects.filter(name='band_0_edited').first()
        self.assertIsNotNone(band_0_edited)
        self.assertEqual(band_0_edited.description, 'edited')
        self.assertEqual(band_0_edited.musicians.first(), auth.get_user(self.client).musician)

        response: HttpResponse = self.client.post(f'{self.BAND_EDIT_URL}{band_0.id + 5}/',
                                                  data=band_data,
                                                  **header)
        self.assertEqual(response.status_code, 404)

    def test_band_delete(self):
        band_0 = Band.objects.filter(name='band_0').first()
        response: HttpResponse = self.client.delete(f'{self.BAND_EDIT_URL}{band_0.id}/')
        self.assertRedirects(response, self.BANDS_DASHBOARD_URL)
        self.assertIsNone(Band.objects.filter(name='band_0').first())

        band_1 = Band.objects.filter(name='band_1').first()
        response: HttpResponse = self.client.delete(f'{self.BAND_EDIT_URL}{band_1.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')
        self.assertIsNotNone(Band.objects.filter(name='band_1').first())

        response: HttpResponse = self.client.delete(f'{self.BAND_EDIT_URL}{band_1.id + 5}/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')


class TestBandsView(TestCase):

    BANDS_URL = reverse(BandsView.name)

    @classmethod
    def setUpClass(cls):
        user = UserFactory.create()
        user.set_password(user.password)
        user.save()
        styles = StyleFactory.create_batch(size=2)
        cities = CityFactory.create_batch(size=2)
        bands = BandFactory.create_batch(size=4, admin=user)

        for band in bands[:2]:
            band.styles.add(styles[0])
            band.city = cities[0]
            band.save()

        for band in bands[2:]:
            band.styles.add(styles[1])
            band.city = cities[1]
            band.save()

    @classmethod
    def tearDownClass(cls):
        User.objects.all().delete()
        City.objects.all().delete()
        Musician.objects.all().delete()
        Band.objects.all().delete()
        Style.objects.all().delete()
        StyleFactory.reset_sequence()
        UserFactory.reset_sequence()
        BandFactory.reset_sequence()
        CityFactory.reset_sequence()
        StyleFactory.reset_sequence()
        UserFactory.reset_sequence()
        InstrumentFactory.reset_sequence()
        InstrumentCategoryFactory.reset_sequence()

    def test_bands_list_view(self):
        response: HttpResponse = self.client.get(self.BANDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/bands.html')
        bands: QuerySet = response.context[0].get('bands')
        self.assertEqual(bands.count(), 4)

    def test_band_detail_view(self):
        band = Band.objects.last()
        response: HttpResponse = self.client.get(f'{self.BANDS_URL}{band.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bands/band.html')
        context_band: Band = response.context[0].get('band')
        self.assertEqual(band, context_band)

        response: HttpResponse = self.client.get(f'{self.BANDS_URL}{band.id + 5}/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_bands_filters(self):
        city = City.objects.first()
        response: HttpResponse = self.client.get(f'{self.BANDS_URL}?city={city.id}')
        self.assertTemplateUsed(response, 'bands/bands.html')
        bands: QuerySet = response.context[0].get('bands')
        self.assertEqual(bands.count(), 2)
        self.assertEqual(bands.order_by('id').all()[0].name, 'band_0')
        self.assertEqual(bands.order_by('id').all()[1].name, 'band_1')

        style = Style.objects.last()
        response: HttpResponse = self.client.get(f'{self.BANDS_URL}?style={style.id}')
        bands: QuerySet = response.context[0].get('bands')
        self.assertEqual(bands.count(), 2)
        self.assertEqual(bands.order_by('id').all()[0].name, 'band_2')
        self.assertEqual(bands.order_by('id').all()[1].name, 'band_3')
