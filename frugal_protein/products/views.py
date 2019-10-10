from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin

from . import models as m
from . import forms

# Create your views here.
class ProductView(DetailView):
    context_object_name = 'product'
    model = m.ProductInfo
    template_name = 'products/product.html'

class SearchView(FormMixin, ListView):
    # FormMixin Attributes
    form_class = forms.ProductSearchForm
    
    # ListView Attributes
    context_object_name = 'products'
    template_name = 'products/product_search.html'
    paginate_by = 24
    
    # FormMixin Methods
    def get_initial(self):
        self.initial = {'search': self.request.GET.get('search')}
        return super().get_initial()

    # ListView Methods
    def get_queryset(self):
        """ Query model based on search query then filter by brand and store """
        search_query = self.request.GET.get('search')
        brand_query = self.request.GET.get('brand')
        store_query = self.request.GET.get('store')

        queryset = []
        if search_query: 
            queryset = m.ProductInfo.objects.filter(description__icontains=search_query).order_by('description')
        
            if brand_query:
                queryset = queryset.filter(brand_id=brand_query)
            if store_query and store_query != 'all':
                kwarg = {store_query + '__isnull': False}
                queryset = queryset.filter(**kwarg)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['querystring'] = self.request.GET
        return context