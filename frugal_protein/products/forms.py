from django import forms
from .models import Brands, ProductInfo

class ProductSearchForm(forms.Form):
    search = forms.CharField(max_length = 255)
    