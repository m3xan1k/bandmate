from django.test import TestCase

from bands.models import City


class TestBands(TestCase):

    @staticmethod
    def test_city_creation():
        city: City = City.objects.create(name='Moscow')

        assert City.objects.count() == 1
        assert city.name == 'Moscow'
