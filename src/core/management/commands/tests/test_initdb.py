from django.test import TestCase
from django.core.management.base import CommandError
from django.contrib.auth.models import User
from job.models import Language, Country, Community, Province, City
from core.management.commands.initdb import (
    Command,
    insert_languages,
    is_language_table_empty,
    insert_locations,
    are_location_tables_empty,
    has_been_the_database_initializing
)


class TestInitDB(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.c = Command()

    def test_insert_languages(self):
        self.assertTrue(is_language_table_empty())
        insert_languages()
        self.assertFalse(is_language_table_empty())
        self.assertTrue(Language.objects.all().count() > 0)

    def test_insert_locations(self):
        self.assertTrue(are_location_tables_empty())
        insert_locations()
        self.assertFalse(are_location_tables_empty())
        self.assertTrue(Country.objects.all().count() > 0)
        self.assertTrue(Community.objects.all().count() == 17)
        self.assertTrue(Province.objects.all().count() == 50)
        self.assertTrue(City.objects.all().count() > 100)

    def test_has_been_the_database_initializing(self):
        self.assertFalse(has_been_the_database_initializing())
        Language.objects.create(name='xxx')
        self.assertFalse(has_been_the_database_initializing())
        Language.objects.all().delete()
        Province.objects.create(id=555, name='xxx')
        self.assertFalse(has_been_the_database_initializing())
        Language.objects.create(name='xxx')
        self.assertTrue(has_been_the_database_initializing())