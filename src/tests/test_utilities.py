import utilities.languages_utilities as lu
import utilities.utilities as u
from django.test import TestCase
import datetime

class TestUtilities(TestCase):

    def test_get_float_list_from_string(self):
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
        self.assertEqual(u.get_text_between_parenthesis('... (test), ( test2)'), ['test', ' test2'])
        self.assertEqual(u.get_text_between_parenthesis('... (test (subtest)) --- (test2)'), ['subtest', 'test2'])
        self.assertEqual(u.get_text_between_parenthesis('... (test (subtest))'), ['subtest'])

    def test_get_a_list_of_enumerates_from_string(self):
        self.assertEqual(u.get_a_list_of_enumerates_from_string("perro, gato y/o tortuga"), ['perro', 'gato', 'tortuga'])
        self.assertEqual(u.get_a_list_of_enumerates_from_string("pink, blue and red; green or black"), ['pink', 'blue', 'red', 'green', 'black'])
        self.assertEqual(u.get_a_list_of_enumerates_from_string("hello world"), ["hello world"])

    def test_get_an_and_list_of_enumerates_from_string(self):
        self.assertEqual(u.get_an_and_list_of_enumerates_from_string("perro, gato y/o tortuga"), ['perro', 'gato y/o tortuga'])
        self.assertEqual(u.get_an_and_list_of_enumerates_from_string("pink, blue and red; green or black"), ['pink', 'blue and red', 'green or black'])
        self.assertEqual(u.get_an_and_list_of_enumerates_from_string("pink, blue y red; green or black"), ['pink', 'blue', 'red', 'green or black'])
        self.assertEqual(u.get_an_and_list_of_enumerates_from_string("se requiere inglés más alemán con francés"), ['se requiere inglés', 'alemán', 'francés'])
        self.assertEqual(u.get_an_and_list_of_enumerates_from_string("hello world"), ["hello world"])

    def test_get_an_or_list_of_enumerates_from_string(self):
        self.assertEqual(u.get_an_or_list_of_enumerates_from_string("perro, gato y/o tortuga o conejo"), ['perro, gato', 'tortuga', 'conejo'])
        self.assertEqual(u.get_an_or_list_of_enumerates_from_string("pink, blue and red; green or black"), ['pink, blue and red; green or black'])
        self.assertEqual(u.get_an_or_list_of_enumerates_from_string("se requiere inglés como alemán - francés"), ['se requiere inglés', 'alemán', 'francés'])
        self.assertEqual(u.get_an_or_list_of_enumerates_from_string("hello world"), ["hello world"])

    def test_find_indexes_apparitions(self):
        self.assertEqual(u.find_indexes_apparitions('calandraca', 'a'), [1,3,7,9])
        self.assertEqual(u.find_indexes_apparitions('calandraca', 'w'), [])

    def test_get_date_from_string(self):
        self.assertEqual(u.get_date_from_string("..... 31-12-2020 ......."), datetime.date(2020,12,31))
        self.assertEqual(u.get_date_from_string("..... 31/12/2020 ......."), datetime.date(2020,12,31))
        self.assertIsNone(u.get_date_from_string("..... veinte de diciembre ......."))

    def test_get_end_index_of_a_paragraph_from_string(self):
        self.assertEqual(u.get_end_index_of_a_paragraph_from_string("0123\n567\n9"), 4)
        self.assertEqual(u.get_end_index_of_a_paragraph_from_string("0123\n567\n9", 4), 4)
        self.assertEqual(u.get_end_index_of_a_paragraph_from_string("0123\n567\n9", 5), 8)
        self.assertEqual(u.get_end_index_of_a_paragraph_from_string("0123"), -1)

    def test_get_slice_from_sub_to_end_of_the_paragraph(self):
        self.assertEqual(u.get_slice_from_sub_to_end_of_the_paragraph('12', "0123\n567\n9"), '3')
        self.assertEqual(u.get_slice_from_sub_to_end_of_the_paragraph("5", "0123\n567\n9"), '67')
        self.assertEqual(u.get_slice_from_sub_to_end_of_the_paragraph("x", "0123\n567\n9"), "")
        self.assertEqual(u.get_slice_from_sub_to_end_of_the_paragraph("12", "01234"), "")

    def test_get_text_before_parenthesis(self):
        self.assertEqual(u.get_text_before_parenthesis('...'), '')
        self.assertEqual(u.get_text_before_parenthesis('hello (  test )'), "hello" )
        self.assertEqual(u.get_text_before_parenthesis('hello (test), ( test2)'), "hello" )

    def test_get_text_after_key(self):
        self.assertEqual(u.get_text_after_key('hola', 'hola amigo  '), 'amigo')
        self.assertEqual(u.get_text_after_key('hola', 'adiós amigo  '), '')

    def test_get_text_before_key(self):
        self.assertEqual(u.get_text_before_key('amigo', ' hola amigo  '), 'hola')
        self.assertEqual(u.get_text_before_key('amigo', 'adiós colega  '), '')

    def test_get_text_before_sub(self):
        # default separators == ['.', '\n', ',']
        self.assertEqual(u.get_text_before_sub("de todos sin duda, Paco era el mejor", 'era', distance=10), "Paco")
        self.assertEqual(u.get_text_before_sub("de todos sin duda, Paco era el mejor", 'era', distance=11, separators=[]), "duda, Paco")
        self.assertEqual(u.get_text_before_sub("de todos sin duda, Paco era el mejor", 'x', distance=10), "")

    def test_get_text_after_sub(self):
        # default separators == ['.', '\n', ',']
        self.assertEqual(u.get_text_after_sub("sin duda, Paco era el mejor, el más listo", 'Paco', distance=20), "era el mejor")
        self.assertEqual(u.get_text_after_sub("sin duda, Paco era el mejor, el más listo", 'Paco', distance=10), "era el me")
        self.assertEqual(u.get_text_after_sub("sin duda, Paco era el mejor, el más listo", 'Paco', distance=10, separators=['el más']), "era el me")
        self.assertEqual(u.get_text_after_sub("sin duda, Paco era el mejor", 'x', distance=10), "")

    def test_get_surrounding_text(self):
        self.assertEqual(u.get_surrounding_text("0123456789", '4', None, 3), "123456789")
        self.assertEqual(u.get_surrounding_text("0123456789", '4', 'x', 3), "123456789")
        self.assertEqual(u.get_surrounding_text("0123456789", '3', '5', 3), "012345678")
        self.assertEqual(u.get_surrounding_text("0123456789", '4', '6', 4), "0123456789")
        self.assertEqual(u.get_surrounding_text("0123456789", '4', '6', 40), "0123456789")
        self.assertEqual(u.get_surrounding_text("0123456789", 'x', '5', 3), "012345678")
        self.assertEqual(u.get_surrounding_text("0123456789", 'x', 'x', 40), "0123456789")

    def test_get_coincidences(self):
        self.assertEqual(u.get_coincidences("123456789", ['1','3', '100']), ['1','3'])
        self.assertEqual(u.get_coincidences("123456789123", ['1','3', '100']), ['1','3','1','3'])
        self.assertEqual(u.get_coincidences("123456789123", ['1','3', '100'], unique_values=True), ['1','3'])
        self.assertEqual(u.get_coincidences("123456789123", ['100']), [])

    def test_replace_multiple(self):
        self.assertEqual(u.replace_multiple('1234', ['1','3'], 'x'), 'x2x4')
        self.assertEqual(u.replace_multiple('234', ['1','3'], 'x'), '2x4')
        self.assertEqual(u.replace_multiple('234', ['100'], 'x'), '234')

    def test_get_acronym(self):
        self.assertEqual(u.get_acronym("Sociedad Limitada"), "SL")
        self.assertEqual(u.get_acronym("sociedad limitada"), "")
        self.assertEqual(u.get_acronym("sociedad limitada", title=True), "SL")