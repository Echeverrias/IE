from .languages_utilities import get_languages_and_levels_pairs

def get_languages_and_levels_pairs_test():
    assert (get_languages_and_levels_pairs('Se requiere inglés fluido y básico de francés')) == [('inglés', 'C1'), ('francés', 'B1')]
    return True