from django import forms
from .models import Brands, ProductInfo

class ProductSearchForm(forms.Form):
    search = forms.CharField(max_length = 255)
    brand = forms.ChoiceField(
        choices = [],
        required = False,
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate brand ChoiceField with brand names associated with products returned by the search query
        # The search query can be found in the 'initial' kwarg when the form is instantiated
        search_query = kwargs['initial'].get('search')
        if search_query:
            self.fields['brand'].choices = self.get_brand_choices(search_query)


    def get_brand_choices(self, search_query):
        """ Returns brands associated with products returned by search query """
        brands = Brands.objects.filter(productinfo__description__icontains=search_query)
        brands = brands.distinct().order_by('brand')
        return [(brand.brand, brand.brand.title()) for brand in brands]