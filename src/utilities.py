import random
from collections import namedtuple
import re
import threading
from time import time as time_
import datetime
import os, sys, traceback

class Lock(object):
    """"
        This is a decorator
        Use: @Lock()
    """

    def __init__(self):
        self.lock = threading.Lock()

    def __call__(self, foo, *args, **kwargs):

        def inner_func(*args, **kwargs):
            with self.lock:
                return foo(*args, **kwargs)
        return inner_func

def get_random_color():
    Color = namedtuple('Color', 'red green blue transparency')
    return Color(round(random.random(),1), round(random.random(),1), round(random.random(),1), max(round(random.random(),1), 0.5))

def get_random_colors_list(size):
    return [get_random_color() for i in range(0, size)]

Colors_list = get_random_colors_list(50)


def get_a_list_of_enumerates_from_string(string):
    try:
        l = re.split(', |; |,|;| y | and | o | or |\n', string)
        l = [i.strip() for i in l]
        return l
    except TypeError as e:
        return []


def get_an_and_list_of_enumerates_from_string(string):
    l = re.split('\.|, | y |; |,|;|más|con|\n', string) # Importante el '\n' al final de la regexp
    l = [i.strip() for i in l if i]
    return l

def get_an_or_list_of_enumerates_from_string(string):
    l = re.split(' o | ó | y/o | e |-|/|\(|\+|como|\n', string) # Importante el '\n' al final de la regexp
    l = [i.strip() for i in l if i]
    return l

def find_indexes_apparitions(string, char):
    return [i for i, c in enumerate(string) if c == char]


def _get_int_or_float_list_from_string(string, float_flag):
    try:
        # Getting the numbers of the string
        numbers = re.findall('(\d[0-9.,]*)', string)
        print(f'numbers: {numbers}')

        # Cleaning the numbers
        numbers_ = []
        for number in numbers:
            dot_indexes = find_indexes_apparitions(number, '.')
            print(f'ii: {dot_indexes}')
            if dot_indexes:
                last_i_dot = dot_indexes[-1]
                last_dot_to_end = number[last_i_dot + 1:len(number)]
                last_dot_to_end_len = len(last_dot_to_end)
                start_to_last_dot = len(number[0:last_i_dot])
                if (last_dot_to_end_len != 3 and not ',' in last_dot_to_end) or (start_to_last_dot > 3 and len(dot_indexes) == 1):
                    number = number[0:last_i_dot] + ',' + number[last_i_dot + 1:len(number)]
            print(f'number: {number}')
            numbers_.append(number)

        # Converting the string numbers to float or int type
        if float_flag:
            numbers_ = list(map(lambda e: float(e.replace('.', '').replace(',', '.')), numbers_))
        else:
            numbers_ = list(map(lambda e: round(float(e.replace('.', '').replace(',', '.'))), numbers_))
    except Exception as e:
        print(f'Error: {e}')
        numbers_ = []
    return numbers_

def get_int_list_from_string(string):
    _get_int_or_float_list_from_string(string, False)


def get_float_list_from_string(string):
    _get_int_or_float_list_from_string(string, True)


def get_date_from_string(string):
    print('#get_date_from_string: %s'%string)
    try:
        date_str = re.findall("[\d]{1,2}[/-][\d]{1,2}[/-][\d]{4}", string)[0]
        print(date_str)
        date_list = re.split('/|-|\n', date_str)
        print(date_list)
        date_list = [int(e) for e in date_list]
        date_list.reverse()
        print(date_list)
        date_date = datetime.date(*date_list)
        print(date_date)
    except:
        date_date = None
    print(date_date)
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

        :param isub: substring to search, it gives the init position of the returned string
        :param text: a string
        :return: a slice of the initial string
    """
    start = text.lower().find(isub)
    if start < 0:
        return ""
    else:
        start = start + len(isub)
    end = self.get_end_index_of_a_paragraph_from_string(text, start)
    return text[start:end+1].strip()



def get_text_between_parenthesis(string):
    """
    Return a list with all the found substrings between parenthesis.
    If the strings doesn't contains parenthesis the function return an empty list

    :param string: a string
    :return: a list
    """
    try:
        print(f'get_text_between_parenthesis({string})');
        text_list = re.findall('\(([\d\w\s-]+)\)', string)
    except TypeError as e:
        print(f'get_text_between_parenthesis -> Error: {e}')
        text_list = []
    print(f'get_text_between_parenthesis -> {text_list}')
    return text_list


def get_text_between_parenthesis_(string):
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
    except Exception as e:
        text = ''
    return text.strip()

def get_text_before_key(key, text):
    try:
        text = re.findall('(.*)%s' % key, text.lower())[0]
    except Exception as e:
        text = ''
    return text.strip()


def get_text_before_sub(text, sub, distance=5, separators=['.', '\n', ',']):
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
    try:
        expected_coincidences = '|'.join(coincidences)
        coincidences_list = re.findall(expected_coincidences, text)
        if unique_values:
            coincidences_list = set(coincidences_list)
            coincidences_list = list(coincidences_list)
        return coincidences_list
    except Exception as e:
        print(f'Error: {e}')
        return []



def replace_multiple(string, olds, new):
    try:
        return re.compile(r"|".join(olds)).sub(new, string)
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
        print();print(f'Acronym of {string}: {acronym}');print()
        return acronym
    except Exception as e:
        return ''

def get_string_number_from_string(string):
    print('#get_string_number_from_string: %s' % string)
    try:
        return re.findall(r'\d+', string)[0]
    except Exception as e:
        print(f'Error get_string_number_from_string({string}): {e}')
        #raise_function_exception(e)
        return ''

def get_int_from_string(string):
    print('#get_int_from_string: %s' % string)
    try:
        return int(get_string_number_from_string(string))
    except Exception as e:
        print(f'Error get_int_from_string({string}): {e}')
        return None



def trace(func):
    def wrapper(*args, **kwargs):
        start = time_()
        print()
        print(f"TRACE START: calling: {func.__name__}() with {args}, {kwargs}")
        func_result = func(*args, **kwargs)
        print(f"TRACE END: {func.__name__}() returned {'...'} in {time_() - start} seconds")
        print()
        return func_result

    return wrapper

def raise_function_exception(description, exception=Exception):
    tb = sys.exc_info()[-1]
    stk = traceback.extract_tb(tb, 1)
    fname = stk[0][2]
    raise exception(f'Error in {fname}: {description}')

def save_error(e, dictionary={}, path='errors.txt'):
    """
    Write in a file the error raised in a function, the function which raises the error
    and an optional dictionary
    Write in a file the error of a funtion
    :param e: error raised
    :param dictionary: dictionary with data
    :param path: path to the file where the error will be stored
    :return:
    """
    tb = sys.exc_info()[-1]
    stk = traceback.extract_tb(tb, 1)
    fname = stk[0][2]
    with open(path, 'a') as f:
        f.write(f'{datetime.datetime.now().strftime("%c")}: \n')
        f.write(f'function: {fname}\n')
        f.write(f'error: {e}\n')
        for k,v in dictionary.items():
            f.write(f'{k}: {v} \n')
        f.write(f'\n\n\n')