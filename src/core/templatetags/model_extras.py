from django import template
from django.forms.models import model_to_dict as m_to_d

register = template.Library()

@register.filter(name='model_to_dict')
def model_to_dict(model_instance):
    return m_to_d(model_instance)

@register.filter(name='model_list_to_dict_list')
def model_list_to_dict_list(model_instances_list):
    return [model_to_dict(instance) for instance in model_instances_list]