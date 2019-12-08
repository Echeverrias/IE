from django import template
from task.models import Task

register = template.Library()

@register.filter(name='percentage')
def percentage(value):
    return format(value, ".2%")

@register.filter(name='is_running')
def is_running(task):
    if not task or not task.pid:
        return False
    else:
        return  task.state == Task.STATE_RUNNING
