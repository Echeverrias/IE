from django import template
import math

register = template.Library()

@register.filter(name='page_range')
def page_range(page_obj, num_pages):
    i = math.ceil(num_pages/2);
    i_left = i - 1
    if num_pages % 2 == 0:
        i_right = i
    else:
        i_right = i - 1
    first_page = max(1, page_obj.number - i_left)
    last_page = max(num_pages, min(page_obj.number + i_right, page_obj.paginator.num_pages))
    r = range(first_page, last_page + 1)
    return r

@register.filter(name='get_attributes')
def get_attributes(dict_list, key):
    attributes = [dict_[key] for dict_ in dict_list]
    return attributes

@register.filter(name='join')
def join(list_, character):
    return character.join(list_)

@register.filter(name='percentage')
def percentage(value):
    return format(value, ".2%")