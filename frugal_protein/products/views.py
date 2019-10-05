from django.shortcuts import render
from django.views.generic import DetailView

from . import models as m

# Create your views here.
class ProductView(DetailView):
    context_object_name = 'product'
    model = m.ProductInfo
    template_name = 'products/product.html'