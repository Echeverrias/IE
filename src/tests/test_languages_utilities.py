import utilities.languages_utilities as lu
from django.test import TestCase

class TestUtilities(TestCase):

    def test_get_languages_and_levels_pairs(self):
        self.assertEqual(lu.get_languages_and_levels_pairs('Se requiere inglés fluido y básico de francés'), [('inglés', 'C1'), ('francés', 'B1')])
        self.assertEqual(lu.get_languages_and_levels_pairs('Se requieren idiomas'), [])