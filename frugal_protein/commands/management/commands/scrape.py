"""
Command for automated webpage scraping and storing/updating results in database.

Scraping types:
    (1) IDs    - scrapes all product barcodes and product ids (pids) of 
                 selected store(s)
    (2) infos  - scrapes all product of selected store(s) for its info 
                 (e.g. description, brand, qty, nutrition)

Positional Args (Required):
    (1) type - [id/info]

Named Args (Optional):
    • -s, --stores    - Overrides default behaviour (scrape all stores), to 
                        instead, scrape selected store(s)
    • -l, --live      - Overrides default setting of using local development db 
                        as source of products for info scraping, to instead use 
                        local backup of live db. 
                        (Only valid for info scraping)
    • -e, --exclusive - Specify which info values to scrape 
                        (Only valid for info scraping)
    • -E, --exclude   - Specify which info values to exclude from scrape
                        (Only valid for info scraping)

Example Usage:
    • scrape ids from all available stores
        py manage.py scrape id

    • scrape ids from tesco
        py manage.py scrape id -s tesco

    • scrape info from tesco and iceland
        py manage.py scrape info -s tesco iceland

    • scrape description and nutrition info for tesco and iceland products
        py manage.py scrape info -s tesco iceland -e description nutriton

    • scrape all info, except image, from tesco
        py manage.py scrape info -s tesco -E image

    • scrape price info for all tesco products on backup of live db
        py manage.py scrape info -s tesco -e price -l
"""

from django.core.management.base import BaseCommand
from django.db.models import Q

import frugal_protein_scrapers as fps
from products.models import Brands, ProductInfo
from ._scrape import ScrapeHandler, STORES



class Command(BaseCommand):
    help = 'scrape product infos'
    valid_stores = STORES

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            'type', 
            nargs=1, type=str, choices=['id', 'info'],
            help='Specify to scrape ids or product info'
        )
        
        # Named arguments
        parser.add_argument(
            '-s', '--stores', 
            nargs='+', type=str, choices=self.valid_stores,
            help='The stores to scrape from'
        )
        parser.add_argument(
            '-l', '--live',
            action='store_true',
            help='Perform info scrape using local version of live_db'
        )
        parser.add_argument(
            '-e', '--exclusive',
            nargs='+', type=str,
            help='Specify which info values to scrape'
        )
        parser.add_argument(
            '-E', '--exclude',
            nargs='+', type=str,
            help='Specify which info values to exclude from info scrape'
        )

    def handle(self, *args, **options):
        handler = ScrapeHandler(*args, **options)
        scrape_type = options['type'][0]
        if scrape_type == 'id':
            handler.execute_id_scrape()
        elif scrape_type == 'info':
            handler.execute_info_scrape()