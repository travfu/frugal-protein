import re
from django import template
from django.utils.safestring import mark_safe


register = template.Library()

@register.filter
def add_class(html, class_string):
    """
    Adds string to class attribute of an html element.
    If input html has multiple elements, only the first element will be
    modified.
    """
    # If input html is not string type, get __str__
    if not isinstance(html, str):
        html = html.__str__()
        
    # If class attribute not present in html, create a new one
    if not 'class=' in html:
        tag = html.split()[0]
        class_value = f'{tag} class="{class_string}"'
        new_html = html.replace(tag, class_value)

    # If class attribute present, append class string to existing class value
    else:
        class_attr = re.compile(r"(?<=class=[\"'])[^\"']*?(?=[\"'])")
        class_value = class_attr.findall(html)[0]
        
        # Assemble new class attribute values
        class_value = class_value.split()
        class_value.append(class_string)
        new_class_value = ' '.join(class_value)

        new_html = class_attr.sub(new_class_value, html)
    
    # Mark string as safe for HTML output
    # https://docs.djangoproject.com/en/2.2/ref/utils/#django.utils.safestring.mark_safe
    return mark_safe(new_html)


if __name__ == '__main__':
    import unittest
    from django.utils.safestring import SafeText

    class TestFilters(unittest.TestCase):
        def test_add_class_no_existing_class(self):
            html = '<input type="number">'
            e_html = '<input class="test" type="number">'
            self.assertEqual(add_class(html, 'test'), e_html)

        def test_add_class_has_existing_class(self):
            html = '<input class="value" type="number">'
            e_html = '<input class="value test" type="number">'
            self.assertEqual(add_class(html, 'test'), e_html)

        def test_add_class_has_special_char(self):
            html = '<input class="some_value-string" type="number">'
            e_html = '<input class="some_value-string test" type="number">'
            self.assertEqual(add_class(html, 'test'), e_html)

        def test_add_class_has_empty_class(self):
            html = '<input class="" type="number">'
            e_html = '<input class="test" type="number">'
            self.assertEqual(add_class(html, 'test'), e_html)

        def test_add_class_returns_SafeText(self):
            html = '<input class="" type="number">'
            self.assertIsInstance(add_class(html, 'test'), SafeText)

    unittest.main()