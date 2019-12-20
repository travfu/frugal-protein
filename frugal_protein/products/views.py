from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import FormMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect

from . import models as m
from . import forms
from .helper.barcode import decode_barcode


class Index(FormMixin, TemplateView):
    template_name = 'products/index.html'
    form_class = forms.ProductSearchForm

    def post(self, request):
        barcode_form = forms.Barcode(request.POST, request.FILES)

        if barcode_form.is_valid:
            img_file = barcode_form.files['barcode_img']
            barcode = decode_barcode(img_file)

            if len(barcode) >= 1:
                try:
                    query_result = m.ProductInfo.objects.get(barcode=barcode[0])
                except ObjectDoesNotExist:
                    context = self.get_context_data(error="Product not found in database")
                    return self.render_to_response(context)
                else:
                    return HttpResponseRedirect(f'product/{query_result.pid}')
        context = self.get_context_data(error="No barcode found in image")
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_barcode'] = forms.Barcode
        return context

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
            # the '__search' in filter() requires django.contrib.postgres
            queryset = m.ProductInfo.objects.filter(
                description__search=search_query).order_by('description')
            if brand_query and brand_query != '0':
                # brand_query value of '0' corresponds to 'all brands'
                queryset = queryset.filter(brand_id=brand_query)
            if store_query and store_query != 'all':
                kwarg = {store_query + '__isnull': False}
                queryset = queryset.filter(**kwarg)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['querystring'] = self.request.GET
        return context

class ProductBrowser(FormMixin, ListView):
    form_class = forms.ProductBrowserForm
    context_object_name = 'products'
    template_name = 'products/product_browser.html'

    def get_initial(self):
        self.initial = {
            'search': self.request.GET.get('search'),
            'store': self.request.GET.get('store')
        }
        return super().get_initial()

    def get_queryset(self):
        search_query = self.request.GET.get('search')
        store = self.request.GET.get('store')

        queryset = []
        if search_query:
            store_filter = {f'{store}__isnull': False}
            queryset = m.ProductInfo.objects.filter(**store_filter)
            queryset = queryset.filter(
                description__search=search_query).order_by('description')

        for product in queryset:
            setattr(product, 'x', product.cheapest_price(store))
        return queryset
