from django import template
from task.models import Task

register = template.Library()

@register.filter(name='is_running')
def is_running(task):
    if not task or not task.pid:
        return False
    else:
        return  task.state == Task.STATE_RUNNING\

@register.filter(name='get_action_form')
def get_action_form(model, model_response):
    if not model_response:
        return './' + model
    elif model == model_response:
        return '.'
    else:
        return '../' + model
