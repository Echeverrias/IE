import random
from collections import namedtuple
import re
import threading
from time import time as time_
import datetime

def get_random_color():
    Color = namedtuple('Color', 'red green blue transparency')
    return Color(round(random.random(),1), round(random.random(),1), round(random.random(),1), max(round(random.random(),1), 0.5))

def get_random_colors_list(size):
    return [get_random_color() for i in range(0, size)]

Colors_list = get_random_colors_list(50)

def get_a_list(string):
    l = re.split('\.|, | y |; |,|;|más|con|\n', string) # Importante el '\n' al final de la regexp
    l = [i.strip() for i in l if i]
    return l

def get_or_list(string):
    l = re.split(' o | ó | y/o | e |-|/|\(|\+|como|\n', string) # Importante el '\n' al final de la regexp
    l = [i.strip() for i in l if i]
    return l

def find_apparitions(string, char):
    return [i for i, c in enumerate(string) if c == char]

def get_int_list(string):
    try:
        numbers = re.findall('(\d[0-9.,]*)', string)
        numbers_ = []
        for number in numbers:
            ii = find_apparitions(number, '.')
            if ii:
                last_i = ii[len(ii) - 1]
            if ii and (last_i + 3) >= len(number):
                number = number[0:last_i] + ',' + number[last_i + 1:len(number)]
            numbers_.append(number)
        numbers_ = list(map(lambda e: round(float(e.replace('.', '').replace(',','.'))), numbers_))
    except Exception as e:
        numbers_ = []
    return numbers_

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
        expected_coincidences = ""
        for i, coincidence in enumerate(coincidences):
            expected_coincidences += coincidence
            if i < len(coincidences) - 1:
                expected_coincidences += '|'
        coincidences_list = re.findall(expected_coincidences, text)
        if unique_values:
            temp = []
            for i in coincidences_list:
                if not i in temp:
                    temp.append(i)
            coincidences_list = temp
        return coincidences_list
    except Exception as e:
        print(f'Error: {e}')
        return []



class Lock(object):

    def __init__(self):
        self.lock = threading.Lock()

    def __call__(self, foo, *args, **kwargs):

        def inner_func(*args, **kwargs):
            with self.lock:
                return foo(*args, **kwargs)
        return inner_func


def replace_multiple(string, olds, new):
    return re.compile(r"|".join(olds)).sub(new, string)


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

def save_error(dictionary, path='errors.txt'):
    with open(path, 'a') as f:
        f.write(f'{datetime}: \n')
        for k,v in dictionary.items():
            f.write(f'{k:} {v}: \n')
        f.write(f'\n')
        f.write(f'\n')

