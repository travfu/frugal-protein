from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import FormMixin

from . import models as m
from . import forms


class Index(FormMixin, TemplateView):
    template_name = 'products/index.html'
    form_class = forms.ProductSearchForm

class ProductView(FormMixin, DetailView):
    context_object_name = 'product'
    model = m.ProductInfo
    template_name = 'products/product.html'
    # Form for navbar
    form_class = forms.ProductSearchForm

class SearchView(FormMixin, ListView):
    # FormMixin Attributes
    form_class = forms.ProductSearchForm
    
    # ListView Attributes
    context_object_name = 'products'
    template_name = 'products/product_search.html'
    paginate_by = 24
    
    # FormMixin Methods
    def get_initial(self):
        self.initial = {
            'search': self.request.GET.get('search'), 
            'brand': self.request.GET.get('brand'),
            'store': self.request.GET.get('store')
        }
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
                if brand_query == '0':
                    # 0 value is assigned to 'all brands'
                    pass
                else:
                    queryset = queryset.filter(brand_id=brand_query)
            if store_query and store_query != 'all':
                kwarg = {store_query + '__isnull': False}
                queryset = queryset.filter(**kwarg)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['querystring'] = self.request.GET
        return context