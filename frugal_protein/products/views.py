from django.shortcuts import render
from django.views.generic import DetailView, ListView

from . import models as m

# Create your views here.
class ProductView(DetailView):
    context_object_name = 'product'
    model = m.ProductInfo
    template_name = 'products/product.html'

class SearchView(ListView):
    queryset = m.ProductInfo.objects.filter(description__icontains = 'quorn')
    context_object_name = 'products'
    template_name = 'products/product_search.html'
    