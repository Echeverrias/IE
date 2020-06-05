from django import template
from task.models import Task

register = template.Library()

@register.filter(name='is_running')
def is_running(task):
    if not task or not task.pid:
        return False
    else:
        return  task.state == Task.STATE_RUNNING

@register.filter(name='get_action_form')
def get_action_form(model, model_response):
    if not model_response:
        return './' + model
    elif model == model_response:
        return '.'
    else:
        return '../' + model

@register.filter(name='verbose_item')
def verbose_item(task):
    d = {
        'ie': 'ofertas de empleo',
        'companies': 'empresas',
    }
    return  d.get(task.name, '')
