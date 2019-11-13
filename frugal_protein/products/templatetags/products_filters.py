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
        'sngl': 'item',
        'l': 'litre'
    }
    
    value = value.lower()
    if any(value == option for option in options):
        return options[value]
    else:
        return value

@register.filter
def format_querystring(query_dict):
    """ Returns querystring from GET request as string (ignore 'page') """
    querystring_lst = []
    for k, v in query_dict.items():
        if k != 'page':
            querystring_lst.append(k + '=' + v)
    querystring = '?' + '&'.join(querystring_lst)
    return querystring