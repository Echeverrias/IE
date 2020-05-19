import os, sys
from .utilities import (
    get_an_and_list_of_enumerates_from_string,
    get_an_or_list_of_enumerates_from_string,
    get_surrounding_text,
    get_coincidences,
)

LANGUAGES = [
    'inglés','francés', 'alemán',
    'italiano', 'ruso', 'chino', 'japonés',
    'canadiense', 'portugués', 'euskera',
    'catalán', 'gallego', 'vasco', 'valenciano',
    'castellano', 'español',
    'danés', 'sueco', 'suizo', 'holandés',
    'noruego', 'finés', 'lapón',
    'rumano', 'polaco', 'eslovaco', 'checo',
    'maltés', 'árabe',
]

def fix_languages(text):
    return text.lower().replace('english', 'inglés').replace('ingles\n', 'inglés\n').replace('ingles ', 'inglés ').replace('ingles,','inglés,').replace('aleman  ', 'alemán ').replace('frances ', 'francés ')

def get_languages(text):
    languages = LANGUAGES
    coincidences = get_coincidences(text, languages, True)
    return coincidences

def get_level_language_equivalent(level, default_level=None):
    level_equivalent= {
        'c2': 'C2',
        'lengua materna': 'C2',
        'segunda lengua': 'C2',
        'nativo': 'C2',
        'bilingue': 'C2',
        'bilingüe': 'C2',
        'muy alto': 'C2',
        'c1': 'C1',
        'dominio': 'C1',
        'domininar': 'C1',
        'alto': 'C1',
        'fluido': 'C1',
        'fluent': 'C1',
        'b2': 'B2',
        'medio alto': 'B2',
        'avanzado': 'B2',
        'medio-alto': 'B2',
        'medio/alto': 'B2',
        'valorará': 'B2',
        'valorable': 'B2',
        'valora': 'B2',
        'segundo idioma': 'B2',
        'b1': 'B1',
        'medio': 'B1',
        'intermedio': 'B1',
        'buen': 'B1',
        'conocimiento': 'A2',
        'a2': 'A2',
        'a1': 'A1',
    }
    return level_equivalent.get(level.lower(), default_level)

def get_levels_language_equivalent(levels, default_level=None):
    return [get_level_language_equivalent(level, default_level) for level in levels]


def get_raw_levels(text):
    levels1 = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']
    levels2 = ['nativo', 'lengua materna', 'segunda lengua', 'first', 'bilingüe', 'bilingue', 'muy alto', 'dominio', 'dominar', 'alto', 'fluido', 'fluent', 'segundo idioma', 'medio alto', 'avanzado', 'medio-alto', 'medio/alto', 'valora', 'valorará', 'valorable', 'medio', 'intermedio', 'buen','conocimiento']
    levels = [*levels1, *levels2]
    coincidences = get_coincidences(text.lower(), levels)
    return coincidences

def get_levels_language(text, default_value='B2'):
    raw_levels = get_raw_levels(text) or [default_value]
    return get_levels_language_equivalent(raw_levels, default_value)

def get_languages_and_levels_pairs(text):
    """
    Look for languages and their levels in the argument 'text'
    :param text: a string
    :return: a list of language-level tuples
    """
    print() ##
    text = fix_languages(text)
    pairs = []
    languages = get_languages(text)
    if len(languages) > 0:
        text_ = get_surrounding_text(text, languages[0], languages[len(languages) - 1], 25)
        if len(languages) > 1:
            languages_ = get_an_and_list_of_enumerates_from_string(text_)
        else:
            languages_ = [text_]
        lng = languages_
        if len(languages_) > len(languages):
            languages_aux = []
            c = set()
            for text in languages_:
                ll = get_languages(text)
                if ll:
                    for l in ll:
                        if not l in c:
                            c.add(l)
                            languages_aux.append(l)
            languages_ = languages_aux
        if len(languages_) < len(languages):
            lang_temp = []
            for language_ in languages_:
                lang_or_l = get_an_or_list_of_enumerates_from_string(language_)
                if (len(lang_or_l) == 1):
                        languages__ = get_languages(lang_or_l[0] + ' ')
                        if languages__:
                            levels = get_raw_levels(lang_or_l[0])
                            if levels:
                                level = levels[0]
                            else:
                                level = ""
                            language_level = languages__[0] + ' ' + level
                            if (not language_level in lang_temp):
                                 lang_temp.append(language_level)
                else:
                    l_temp = []
                    level_temp = ''
                    for l in lang_or_l:
                        try:
                            language = get_languages(l + ' ')[0]
                            levels = get_raw_levels(l) or get_raw_levels(language_)
                            if levels:
                                level = levels[0]
                            else:
                                level = ""
                            language_level = language + ' ' + level
                            if not language_level in l_temp:
                                l_temp.append(language_level)
                        except:
                            language_ = language_.replace(l, '')
                    for l in l_temp:
                        if not l in lang_temp:
                            lang_temp.append(l)
                languages_ = lang_temp
        if len(languages_) == len(languages):
            levels = [get_levels_language(text, 'B1')[0] for text in languages_]
            pairs = list(zip(languages, levels))
        else:
            with open('../languages_p.txt', 'a') as f:
                f.write(text + '\n')
                f.write(str(languages) + '\n')
                f.write(text_ + '\n')
                f.write(str(lng) + '\n')
                f.write(str(languages_) + '\n')
                f.write('\n')
                f.write('\n')
    return pairs