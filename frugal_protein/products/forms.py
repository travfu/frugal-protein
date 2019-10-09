from django import forms
from .models import Brands, ProductInfo

class ProductSearchForm(forms.Form):
    search = forms.CharField(max_length = 255)
    brand = forms.ChoiceField(
        choices = [],
        required = False,
    )
    store = forms.ChoiceField(
        choices = [],
        required = False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Goal: 
        #   1) populate brand dropdown with brand name of products returned by search query
        #   2) populate store dropdown with a list of all the stores (independent of search query) 

        # The search query can be found in the 'initial' kwarg when the form is instantiated
        search_query = kwargs['initial'].get('search')
        if search_query:
            self.fields['brand'].choices = self.get_brand_choices(search_query)

        self.fields['store'].choices = self.get_store_choices()

    def get_brand_choices(self, search_query):
        """ Returns brands associated with products returned by search query """
        brands = Brands.objects.filter(productinfo__description__icontains=search_query)
        brands = brands.distinct().order_by('brand')
        return [(brand.brand, brand.brand.title()) for brand in brands]

    def get_store_choices(self):
        """ Returns list of stores """
        stores = ['tesco', 'iceland']
        choice_tuples = [(store, store.title()) for store in stores]
        choice_tuples.insert(0, ('all', 'All Stores'))
        return choice_tuples