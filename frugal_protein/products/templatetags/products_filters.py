from django import template


register = template.Library()

@register.filter
def formatprice(value):
    """
    Formats value to add pound symbol prefix,
    but if value is string, return string
    """
    try:
        price = float(value)
    except ValueError:
        # str but not a price value (i.e. contains char not accepted by float())
        return value
    except TypeError:
        # If not string/int/float, return empty string
        return ''
    else:
        return '£' + f'{price:.2f}'

@register.filter
def formatuom(value):
    """Translates measurement units to reader-friendly text"""
    options = {
        'sngl': 'item',
        'l': 'litre'
    }
    if value:
        value = value.lower()
        if value in options:
            return options[value]
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