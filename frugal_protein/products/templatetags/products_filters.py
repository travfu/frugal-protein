from django import template


register = template.Library()

@register.filter
def formatprice(value):
    """
    Formats value to add pound symbol prefix,
    but if value is string, return string
    """
    if value is not None:
        if type(value) == str:
            return value
        else:            
            return '£' + f'{value:.2f}'
    return ''