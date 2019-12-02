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

from products.models import Brands, ProductInfo

from frugal_protein_scrapers.scrapers import scrape_ids


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
        pass
    

    def scrape_infos(self, stores=None):
        pass
    

    def scrape_prices(self, stores=None):
        pass
        

