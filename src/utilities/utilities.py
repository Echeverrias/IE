import random
from collections import namedtuple
import re
import datetime
import logging
logging.getLogger().setLevel(logging.INFO)

def get_random_color():
    Color = namedtuple('Color', 'red green blue transparency')
    return Color(round(random.random(),1), round(random.random(),1), round(random.random(),1), max(round(random.random(),1), 0.5))

def get_random_colors_list(size):
    return [get_random_color() for i in range(0, size)]

Colors_list = get_random_colors_list(50)

def get_a_list_of_enumerates_from_string(string):
    try:
        l = re.split(', |; |,|;| y | and | o | or | y/o | - |\n', string)
        l = [i.strip() for i in l]
        return l
    except TypeError as e:
        return []

def get_an_and_list_of_enumerates_from_string(string):
    l = re.split('\.|, | y |; |,|;|más|con|\n', string)
    l = [i.strip() for i in l if i]
    return l

def get_an_or_list_of_enumerates_from_string(string):
    l = re.split(' o | ó | y/o | e |-|/|\(|\+|como|\n', string)
    l = [i.strip() for i in l if i]
    return l

def find_indexes_apparitions(string, char):
    return [i for i, c in enumerate(string) if c == char]

def _get_int_or_float_list_from_string(string, float_flag):
    try:
        # Getting the numbers of the string
        numbers = re.findall('(\d[0-9.,]*)', string)
        # Cleaning the numbers
        numbers_ = []
        for number in numbers:
            dot_indexes = find_indexes_apparitions(number, '.')
            if dot_indexes:
                last_i_dot = dot_indexes[-1]
                last_dot_to_end = number[last_i_dot + 1:len(number)]
                last_dot_to_end_len = len(last_dot_to_end)
                start_to_last_dot = len(number[0:last_i_dot])
                if (last_dot_to_end_len != 3 and not ',' in last_dot_to_end) or (start_to_last_dot > 3 and len(dot_indexes) == 1):
                    number = number[0:last_i_dot] + ',' + number[last_i_dot + 1:len(number)]
            numbers_.append(number)
        # Converting the string numbers to float or int type
        if float_flag:
            numbers_ = list(map(lambda e: float(e.replace('.', '').replace(',', '.')), numbers_))
        else:
            numbers_ = list(map(lambda e: round(float(e.replace('.', '').replace(',', '.'))), numbers_))
    except Exception as e:
        numbers_ = []
    return numbers_

def get_int_list_from_string(string):
    return _get_int_or_float_list_from_string(string, False)

def get_float_list_from_string(string):
    return _get_int_or_float_list_from_string(string, True)

def get_date_from_string(string):
    try:
        date_str = re.findall("[\d]{1,2}[/-][\d]{1,2}[/-][\d]{4}", string)[0]
        date_list = re.split('/|-|\n', date_str)
        date_list = [int(e) for e in date_list]
        date_list.reverse()
        date_date = datetime.date(*date_list)
    except:
        date_date = None
    return date_date

def get_end_index_of_a_paragraph_from_string(text, start=0):
    """

        :param text: a string
        :param start: the index of the start position
        :return: the index of the new line character or the last character
    """
    return min(len(text) - 1, text.find('\n', start))

def get_slice_from_sub_to_end_of_the_paragraph(isub, text):
    """
        Look for a substring in a string and if the substring exist, the function return the text after the substring and
        until the end of the paragraph. If the subtring doesnt exist return ''
        :param isub: substring to search, it gives the init position of the returned string
        :param text: a string
        :return: a slice of the initial string
    """
    start = text.lower().find(isub)
    if start < 0:
        return ""
    else:
        start = start + len(isub)
    end = get_end_index_of_a_paragraph_from_string(text, start)
    return text[start:end+1].strip()

def get_text_between_parenthesis(string):
    """
    Return a list with all the found substrings between parenthesis.
    If the strings doesn't contains parenthesis the function return an empty list

    :param string: a string
    :return: a list
    """
    try:
        text_list = re.findall('\(([\d\w\s-]+)\)', string)
    except TypeError as e:
        text_list = []
    return text_list

def _get_text_between_parenthesis(string):
    """
    DEPRECATED
    :param string:
    :return:
    """

    try:
        text = re.search('\(.*?\)', string)
        if text:
            text = text[0]
            text = text[text.find("(") + 1:text.find(")")]
        else:
            text = None
    except:
        text = None
    return text

def get_text_before_parenthesis(string):
    text = string
    while True:
        try:
            text = re.findall('(.+)\(', text)[0].strip()
        except TypeError as e:
            text = ''
            break
        except IndexError as e:
            if text == string:
                text = ''
            break
    return text

def get_text_after_key(key, text):
    try:
        text = re.findall('%s(.*)' % key, text.lower())[0]
    except Exception:
        text = ''
    return text.strip()

def get_text_before_key(key, text):
    try:
        text = re.findall('(.*)%s' % key, text.lower())[0]
    except Exception:
        text = ''
    return text.strip()

def get_text_before_sub(text, sub, distance=5, separators=['.', '\n', ',']):
    """
    A substring is looked for into a text. If exists, from its index is taken a substring with length equal to distance,
    in the left part, to create a new string. If separators has strings, they are looking for in the new substring.
    If a string from the list exist in the new substring, another substring is created that starts from the string list
    founded until the end.

    :param text: a string.
    :param sub: a string. A subtring to look into text param
    :param distance: a integer. The length of the new substring to return.
    :param separators: a list of strings. Look these stings in the new substring.
    :return: a string. A substring with the text before the substring 'sub' in the 'text' variable.
    """
    i = text.lower().find(sub.lower())
    if i <=0:
        return ""
    else:
        i_left = max(0, i - distance)
        i_separators = [text[i_left:i].find(separator) for separator in separators]
        i_separators = [i + i_left + 1 for i in i_separators if i >= 0]
        if i_separators:
            i_left = max(i_left, *i_separators)
    return text[i_left:i].strip()

def get_text_after_sub(text, sub, distance=5, separators=['.', '\n', ',']):
    """
        A substring is looked for into a text. If exists, from its index is taken a substring with length equal to distance,
        in the right part, to create a new string. If separators has strings, they are looking for in the new substring.
        If a string from the list exist in the new substring, another substring is created that starts from the string list
        founded until the end.

        :param text: a string.
        :param sub: a string. A subtring to look into text param
        :param distance: a integer. The length of the new substring to return.
        :param separators: a list of strings. Look these stings in the new substring.
        :return: a string. A substring with the text before the substring 'sub' in the 'text' variable.
        """
    i_sub = text.lower().find(sub.lower())
    if i_sub <0 or (i_sub + len(sub) == len(text)):
        return ""
    else:
        i_start = i_sub + len(sub)
        i_right = min(i_start + distance, len(text))
        i_separators = [text[i_start:i_right].find(separator) for separator in separators]
        i_separators = [i_start + i for i in i_separators if i >= 0]
        if i_separators:
            i_right = min(i_right, *i_separators)
    return text[i_start:i_right].strip()

def get_surrounding_text(text, sub_start, sub_end=None, distance=25):
    """
    Looks for the substrings, 'sub_start' and 'sub_end' variables in 'text' and return a new substring
    with a number equal to 'distance' characters in the left of 'sub_start' position and in the right of
    'sub_end' position if they exist, if one of them are not found the partition of the string will be until
    the start or until the end of the text variable.
    :param text: a string. The string to look for.
    :param sub_start: a string. The start to get the left and the right parts of the new subtring.
    :param sub_end: an optional string. The start to get the right part of the new substring.
    :param distance: an optional integer. The length of the left and right parts of the new string from sub_start
        and sub_end if they are found. If the substrings are not found, the distance will be to the start of the text
        and the end of the text.
    :return: a string. A new substring with the characters around the 'sub_start' and 'sub-end' substrings.
    """
    surrounding_text = ""
    separators = ['.', '\n', ',']
    i_start = text.lower().find(sub_start.lower())
    i_left = max(0, i_start - distance)
    i_separators = [text[i_left:i_start].find(separator) for separator in separators]
    i_separators = [i + i_left + 1 for i in i_separators if i >= 0]
    if i_separators:
        i_left = max(i_left, *i_separators)
    if sub_end:
        i_end = text.lower().find(sub_end.lower())
    else:
        i_end = -1
        sub_end = sub_start
    if i_end < 0:
        i_end = i_start + len(sub_start)
        i_right = len(text)
    else:
        i_end = i_end + len(sub_end)
        i_right= min(len(text), i_end + distance)
    i_separators = [text[i_end:i_right].find(separator) for separator in separators]
    i_separators = [i + i_end for i in i_separators if i >= 0]
    if i_separators:
        i_right = min(i_right, *i_separators)
    surrounding_text = text[i_left:i_right].strip()
    return surrounding_text

def get_coincidences(text, coincidences, unique_values = False):
    """
    Looks for the coincidences list strings in the text variable and return a list with the coincidences.
    :param text: a string
    :param coincidences: a list of strings. The strings to looking for in the text.
    :param unique_values: a boolean. True is we want to return duplicates values found.
    :return: a list of strings. The coincidences list strings found in text
    """
    try:
        expected_coincidences = '|'.join(coincidences)
        coincidences_list = re.findall(expected_coincidences, text)
        if unique_values:
            uniques = []
            for e in coincidences_list:
                if e not in uniques:
                    uniques.append(e)
            coincidences_list = uniques
        return coincidences_list
    except Exception as e:
        return []

def replace_multiple(string, lolds, snew):
    """
     Replaces the 'old' list strings in 'text' for the 'new' string.
    :param string: a string.
    :param lolds: a list of strings. The substrings t looking for in string variable.
    :param snew: a string. The string to replace for olds list strings.
    :return: a string. The new string where the old lists strings have been replaced teh new string.
    """
    try:
        return re.compile(r"|".join(lolds)).sub(snew, string)
    except Exception as e:
        if not string:
            string = ''
        return str(string)

def get_acronym(string, title=False):
    try:
        acronym = string
        if title:
            acronym = acronym.title()
        acronym = ''.join(re.findall(r'[A-ZÁÉÍÓÚ]', acronym))
        acronym = acronym.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        return acronym
    except Exception:
        return ''

def get_string_number_from_string(string):
    try:
        return re.findall(r'\d+', string)[0]
    except Exception:
        return ''

def get_int_from_string(string, default=None):
    """
    Look for a number in the 'string' argument an cast it to an int.
    If not number is found return the value of 'default' argument.
    :param string: a string where the number is looked
    :param default: a value to return if there is no number in string
    :return: a number or None
    """
    try:
        return int(get_string_number_from_string(string))
    except Exception:
        return default