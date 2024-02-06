from django import template

register = template.Library()

@register.filter
def all_completed(tasks):
    return all(task.status == 'COMPLETED' for task in tasks)