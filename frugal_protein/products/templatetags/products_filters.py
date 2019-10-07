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

@register.filter
def formatuom(value):
    """Translates measurement units to reader-friendly text"""
    options = {
        'SNGL': 'item',
        'l': 'litre'
    }
    
    if any(value == option for option in options):
        return options[value]
    else:
        return value