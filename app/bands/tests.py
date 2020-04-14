from django.test import TestCase

from bands.models import (
    City, InstrumentCategory, Instrument,
)


class TestBands(TestCase):

    @staticmethod
    def test_city_creation():
        city: City = City.objects.create(name='Moscow')

        assert City.objects.count() == 1
        assert city.name == 'Moscow'

    @staticmethod
    def test_instruments_and_categories_creation():
        # create new category
        category = InstrumentCategory.objects.create(name='strings')

        # add new instrument related to category
        guitar = Instrument(name='guitar', category=category)
        bass = Instrument(name='bass guitar', category=category)
        drums = Instrument(name='drums')
        Instrument.objects.bulk_create([guitar, bass, drums])

        assert category.instruments.count() == 2
        assert Instrument.objects.count() == 3
        assert category.instruments.first().name == 'guitar'
        assert category.instruments.last().name == 'bass guitar'
        assert guitar.category.name == 'strings'
        assert drums.category is None
