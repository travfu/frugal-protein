"""
Collection of functions to implement the scrape command
"""
import io
import logging
import os
from datetime import date

import boto3

from django.core.files import File
from django.core.management.base import CommandError
from django.db.models import Q

import frugal_protein_scrapers as fps
from frugal_protein import settings
from products.models import ProductInfo, Brands


# Setup logging
filename = f'{date.today()}_infoscrape.log'
filepath = os.path.join(settings.BASE_DIR, 'commands', 'logs', filename)
logging.basicConfig(filename=filepath,level=logging.INFO)

# Lists all stores that is currently supported (i.e. stores that can be scraped)
STORES = frozenset(['tesco', 'iceland'])

class Util:
    """ 
    Collection of functions to support 'scrape' command handling by Handle class 
    """
    @staticmethod
    def stringify(lst):
        return ' '.join(lst).lower() if lst is not None else ''

    @staticmethod
    def valid_id_dict(id_dict):
        """ id_dict containing empty values should return False """
        if id_dict['pid'] is None:
            # {'barcode': '11', 'pid': None}
            # {'barcode': None, 'pid': None}
            return False
        else:
            # {'barcode': '11', 'pid': '22'}
            # {'barcode': None, 'pid': '22'}
            return True

    @staticmethod
    def get_brand_obj(brand):
        """ Returns a Brands object """
        existing_brand = Brands.objects.filter(brand=brand)
        if existing_brand:
            return existing_brand[0]
        else:
            return Brands.objects.create(brand=brand)

    @staticmethod
    def prepend_dict_keys(price_dict, store):
        """ Prepend dict keys with store name """
        new_price_dict = {}
        for k in price_dict:
            new_price_dict[f'{store}_{k}'] = price_dict[k]
        return new_price_dict

    @staticmethod
    def save_local_img(Image, filename):
        """ Save an Image file to local media directory and return path """
        path = os.path.join(settings.MEDIA_ROOT, 'product_images', filename)
        Image.save(path, formate='JPEG', quality=95)
        return path
    
    @staticmethod
    def upload_to_s3(filename):
        """ Upload media file to S3 bucket """
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )
        path = os.path.join(settings.BASE_DIR, 'media', 'product_images', 
                            filename)
        bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')
        destination = f'product_images/{filename}'
        try:
            s3.upload_file(path, bucket, destination)
        except Exception as e:
            raise Exception(e)


class ScrapeHandler:
    """
    A plugin class to handle the scrape command

    Usage:
        >>> handler = ScrapeHandler(*args, **options)
        >>> handler.execute_id_scrape()
        >>> handler.execute_info_scrape()
    """
    util = Util

    def __init__(self, *args, **options):
        # self.type = options['type'][0] # str
        self.stores = options['stores'] or STORES # list
        self.live = options['live'] # bool
        self.exclusive = self.util.stringify(options['exclusive']) # str
        self.exclude = self.util.stringify(options['exclude']) # str

    def execute_id_scrape(self):
        for store in self.stores:
            for id_dicts in fps.scrape_ids(store):
                for id_dict in id_dicts:
                    if self.util.valid_id_dict(id_dict):
                        self._update_ids(id_dict, store)
                

    def execute_info_scrape(self):
        for store in self.stores:
            store_filter = {f'{store}__isnull': False}
            if self.live:
                products = ProductInfo.objects.using('live').filter(**store_filter)
            else:
                products = ProductInfo.objects.filter(**store_filter)
            for product in products:
                pid = getattr(product, store)
                try:
                    info_dict = fps.scrape_infos(pid, store, 
                                                exclusive=self.exclusive, 
                                                exclude=self.exclude)
                    self._update_infos(info_dict, product, store)
                except Exception as e:
                    logging.info(f'{store}({pid}) -- {e}')


    def _update_ids(self, id_dict, store):
        if not self.util.valid_id_dict(id_dict):
            return
        # pid key is renamed to store name to match model field
        id_dict[store] = id_dict.pop('pid')
        barcode = id_dict['barcode']
        store_pid = id_dict[store]

        try:
            if self.live:
                product = ProductInfo.objects.using('live').get(
                    Q(barcode=barcode) | Q(**{store:store_pid})
                )
            else:
                product = ProductInfo.objects.get(
                    Q(barcode=barcode) | Q(**{store:store_pid})
                )
        except ProductInfo.DoesNotExist:
            ProductInfo.objects.create(**id_dict)
        except ProductInfo.MultipleObjectsReturned:
            # If multiple objects returned, it means that there exists multiple
            # products that share either the same barcode but not store pid or 
            # vice versa. 
            # This should not happen, but if it does, log it for further
            # investigation as it may indicate poor db integrity.
            # TODO
            pass
        else:
            store_field = getattr(product, store)
            if product.barcode and not store_field:
                setattr(product, store, store_pid)
                if self.live:
                    product.save(using='live')
                else:
                    product.save()
            elif not product.barcode and store_field:
                product.barcode = barcode
                if self.live:
                    product.save(using='live')
                else:
                    product.save()

    
    def _update_infos(self, info_dict, product, store):
        """ 
        Updates row by replacing empty field values with scraped values 
        See ProductInfo model for attribute names.
        """
        p = product
        i = info_dict

        if not p.description and i.get('description'):
            p.description = i['description']
        
        if not p.brand and i.get('brand'):
            p.brand = self.util.get_brand_obj(i['brand'])

        if not p.qty and i.get('qty'):
            q = i['qty']
            p.qty = q['qty']
            p.num_of_units = q['num_of_units']
            p.total_qty = q['total_qty']
            p.unit_of_measurement = q['unit_of_measurement']
        
        if not p.protein and i.get('nutrition'):
            n = i['nutrition']
            p.header = n['header']
            p.kcal = n['kcal']
            p.fat = n['fat']
            p.carb = n['carb']
            p.protein = n['protein']

        # store-specific prices
        store_price = f'{store}_base_price'
        if not getattr(p, store_price) and i.get('price'):
            price_dict = self.util.prepend_dict_keys(i['price'], store)
            
            for k, v in price_dict.items():
                setattr(p, k, v)
        
        # image: save (if local) and upload to s3
        if (p.img.name.endswith('default.png') or not p.img) and i.get('img'):
            filename = f'{p.pid}.jpg'
            path = self.util.save_local_img(i['img'], filename)
            self.util.upload_to_s3(filename)
            p.img = path

        p.save()
