from django import template

register = template.Library()

@register.filter(name='percentage')
def percentage(value):
    return format(value, ".2%")
