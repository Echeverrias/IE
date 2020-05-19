import utilities.languages_utilities as lu
import utilities.utilities as u
from django.test import TestCase

class TestUtilities(TestCase):

    def execute(self):
        self.get_languages_and_levels_pairs_test()
        self.get_float_list_from_string_test()
        self.get_int_list_from_string_test()

    def test_get_languages_and_levels_pairs_test(self):
        self.assertEqual (lu.get_languages_and_levels_pairs('Se requiere inglés fluido y básico de francés'), [('inglés', 'C1'), ('francés', 'B1')])
        return True

    def test_get_float_list_from_string_test(self):
        self.assertEqual(u.get_float_list_from_string("entre 43,550€ a  45,600€;.."), [43.55, 45.6])
        self.assertEqual(u.get_float_list_from_string("entre 43.550€ a  45.600€;.."), [43550.0, 45600.0])
        self.assertEqual(u.get_float_list_from_string("entre 43.55€ a  45.60€;.."), [43.55, 45.60])

    def test_get_int_list_from_string_test(self):
        self.assertEqual(u.get_int_list_from_string("entre 43.55€ a  45.60€;.."), [44, 46])
        self.assertEqual(u.get_int_list_from_string("entre 43.550€ a  45.600€;.."), [43550, 45600])
        self.assertEqual(u.get_int_list_from_string("entre 43550€ a  45600€;.."), [43550, 45600])
        self.assertEqual(u.get_int_list_from_string("entre 43,550€ a  45,600€;.."), [44, 46])

    def test_get_string_number_from_string(self):
        self.assertEqual(u.get_string_number_from_string('Ver todas sus ofertas (397)'), '397')
        self.assertEqual(u.get_string_number_from_string('Ver todas sus ofertas'), '')

    def test_get_int_from_string(self):
        self.assertEqual(u.get_int_from_string('Ref: 2622727'), 2622727)
        self.assertEqual(u.get_int_from_string('Ver todas sus ofertas (397)', -1), 397)
        self.assertEqual(u.get_int_from_string('Ver todas sus ofertas (397)'), 397)
        self.assertEqual(u.get_int_from_string('Ver todas sus ofertas'), None)
        self.assertEqual(u.get_int_from_string('Ver todas sus ofertas', -1), -1)

    def test_get_text_between_parenthesis(self):
        self.assertEqual(u.get_text_between_parenthesis('...'), [])
        self.assertEqual(u.get_text_between_parenthesis('... (  test )'), ['  test '])
        self.assertEqual(u.get_text_between_parenthesis('... (test)'), ['test'])
        self.assertEqual(u.get_text_between_parenthesis('... (test (subtest))'), ['test (subtest)'])
        self.assertEqual(u.get_text_between_parenthesis('... (test (subtest)) --- (test2)'), ['test (subtest)', 'test2'])


