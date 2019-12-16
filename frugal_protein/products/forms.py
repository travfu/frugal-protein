from django import forms
from .models import Brands, ProductInfo

class myWidget(forms.Select):
    """
    forms.Select generates an html string for <select> froms with <options> and 
    applies user-specified attributes across all <options>. 

    This custom widget add the 'disabled' attribute to <options> with a specific 
    value.
    doc: https://github.com/django/django/blob/master/django/forms/widgets.py
    """
    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        for _, option, _ in context['widget']['optgroups']:
            value = option[0].get('value')
            if value == '':
                option[0]['attrs']['disabled'] = ''
        return context


class ProductSearchForm(forms.Form):
    search = forms.CharField(
        max_length = 255,
        widget = forms.TextInput({
            'class': 'form_field',
            'placeholder': 'search',
        })
    )
    brand = forms.ChoiceField(
        choices = [],
        required = False,
        widget = myWidget({
            'class': 'form_field',
            'onchange': 'this.form.submit()',
        })
    )
    store = forms.ChoiceField(
        choices = [],
        required = False,
        widget = forms.Select({
            'class': 'form_field',
            'onchange': 'this.form.submit()',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Goal: 
        #   1) populate brand dropdown with brand name of products returned by 
        #      search query
        #   2) populate store dropdown with a list of all the stores 
        #      (independent of search query) 

        # The search query can be found in the 'initial' kwarg when the form is 
        # instantiated
        search_query = kwargs['initial'].get('search')
        if search_query is not None:
            self.fields['brand'].choices = self.get_brand_choices(search_query)
        else: 
            self.fields['brand'].choices = [('', 'No Brands')]

        self.fields['store'].choices = self.get_store_choices()

    def get_brand_choices(self, search_query):
        """ Returns brands associated with products returned by search query """
        brands = Brands.objects.filter(
            productinfo__description__search=search_query)
        brands = brands.distinct().order_by('brand')

        choice_tuples = [(b.brand_id, b.brand.title()) for b in brands]
        if choice_tuples:
            brand_count_str = str(len(choice_tuples))
            # Assign value '0' for 'all brands'
            choice_tuples.insert(0, ('0', f'All Brands ({brand_count_str})'))
            choice_tuples.insert(0, ('', f"Select a brand"))
        else:
            choice_tuples = [('', 'No Brands')]
            
        return choice_tuples

    def get_store_choices(self):
        """ Returns list of stores """
        stores = ['tesco', 'iceland']
        choice_tuples = [(store, store.title()) for store in stores]
        choice_tuples.insert(0, ('all', 'All Stores'))
        return choice_tuples


class Barcode(forms.Form):
    barcode_img = forms.ImageField(
        label = "",
        widget = forms.ClearableFileInput(
            {
                'onchange':'this.form.submit()',
                'class': 'barcode-input'
            }
        )
    )