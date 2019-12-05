"""
Command for automated webpage scraping and storing/updating results in database.

Scraping types:
    (1) IDs    - scrapes all product barcodes and product ids (pids) of 
                 selected store(s)
    (2) infos  - scrapes all product of selected store(s) for its info 
                 (e.g. description, brand, qty, nutrition)
    (3) prices - scrapes all products of selected store(s) for its price values

Example Usage:
    • scrape ids from all available stores
        py manage.py scrape id -a

    • scrape ids from tesco
        py manage.py scrape id -s tesco

    • scrape info from tesco and iceland
        py manage.py scrape info -s tesco iceland

Design Restrictions:
    • command must provide scraping type arg
    • command must provide stores to scrape from (either via -a or -s params)
"""

from django.core.management.base import BaseCommand
from django.db.models import Q

from frugal_protein_scrapers.scrapers import scrape_ids, scrape_infos
from products.models import Brands, ProductInfo


class Command(BaseCommand):
    help = 'scrape product infos'
    valid_stores = ['tesco', 'iceland',]

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'type', 
            nargs=1, type=str, choices=['id', 'info', 'price'],
            help='Defines what to scrape'
        )
        
        # Named arguments
        # Mutually exclusive arguments
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '-a', '--all', 
            action='store_true',
            help='Scrapes from all available stores'
        )
        group.add_argument(
            '-s', '--store', 
            nargs='+', type=str, choices=self.valid_stores,
            help='The stores to scrape from'
        )


    def handle(self, *args, **options):
        scrape_type = options['type'][0]
        scrape_all = options['all']
        stores = options['store']

        if scrape_type == 'id':
            if scrape_all:
                self.scrape_ids()
            else:
                self.scrape_ids(stores)
        
        elif scrape_type == 'info':
            if scrape_all:
                self.scrape_infos()
            else:
                self.scrape_infos(stores)
        
        elif scrape_type == 'price':
            if scrape_all:
                self.scrape_prices()
            else:
                self.scrape_prices(stores)


    def scrape_ids(self, stores=None):
        stores = stores or self.valid_stores
        for store in stores:
            for id_dicts in scrape_ids(store):
                # save/update results
                pass
    

    def scrape_infos(self, stores=None):
        stores = stores or self.valid_stores        
        for store in stores[:1]:
            products = self.get_rows_for_info_scrape(store)
            for product in products[:1]:
                # Store pids are stored in fields named after store
                pid = getattr(product, store)
                info_dict = scrape_infos(pid, store)
                self.update_info_result(info_dict, product)
    

    def scrape_prices(self, stores=None):
        stores = stores or self.valid_stores
        for store in stores:
            products = self.get_rows_for_price_scrape(store)
            for product in products[:1]:
                # Store pids are stored in fields named after store
                pid = getattr(product, store)
                info_dict = scrape_infos(pid, store, price_only=True)
                price_dict = info_dict['price_dict']
                price_dict = self.prepend_dict_keys(price_dict, store)
                self.update_price_result(price_dict, product)
                

    def prepend_dict_keys(self, price_dict, store):
        """ Prepend dict keys with store name """
        new_price_dict = {}
        for k in price_dict:
            new_price_dict[f'{store}_{k}'] = price_dict[k]
        return new_price_dict

        

    def get_rows_for_info_scrape(self, store):
        """ 
        Returns a queryset for products associated with a store that require
        info scraping (i.e. have missing info values)        
        """
        store_filter = {f'{store}__isnull': False}
        rows = ProductInfo.objects.filter(**store_filter)
        rows = rows.filter(Q(description='') | 
                           Q(qty__isnull=True) |
                           Q(protein__isnull=True)) # Q allows use of 'or'
        return rows
    
    def get_rows_for_price_scrape(self, store):
        """ 
        Returns queryset of products that have all required fields 
        (i.e. no missing info values)
        """
        store_filter = {f'{store}__isnull': False}
        rows = ProductInfo.objects.filter(**store_filter)
        rows = rows.filter(Q(description__isnull=False) &
                           Q(qty__isnull=False) &
                           Q(protein__isnull=False))
        return rows

    
    def update_info_result(self, info_dict, product):
        """ Updates row by replacing empty field values with scraped values """
        qty = info_dict.get('qty_dict')
        nutrition = info_dict.get('nutrition_dict')
        
        if not product.description and info_dict.get('description'):
            product.description = info_dict['description']

        if not product.brand and info_dict.get('brand'):
            product.brand = self.get_brand_object(info_dict['brand'])

        if not product.qty and qty:
            product.qty = qty['qty']
            product.num_of_units = qty['num_of_units']
            product.total_qty = qty['total_qty']
            product.unit_of_measurement = qty['unit_of_measurement']

        if not product.protein and nutrition:
            product.header = nutrition['header']
            product.kcal = nutrition['kcal']
            product.fat = nutrition['fat']
            product.carb = nutrition['carb']
            product.protein = nutrition['protein']
        
        product.save()

    def get_brand_object(self, brand):
        """ Returns a Brands object """
        existing_brand = Brands.objects.filter(brand=brand)
        if existing_brand:
            return existing_brand[0]
        else:
            return Brands.objects.create(brand=brand)
    
    def update_price_result(self, price_dict, product):
        for k, v in price_dict.items():
            setattr(product, k, v)
        product.save()