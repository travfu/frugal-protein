from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from products.models import ProductInfo, Brands
from scrape.management.commands.scrape import Command
from scrape.management.commands._handlers import ScrapeHandler, STORES, Util


class TestScrapeUtil(TestCase):
    def test_valid_id_dict(self):
        # Valid
        case_1 = {'barcode': '123', 'pid': '234'}
        case_2 = {'barcode': None, 'pid': '234'}
        # Invalid
        case_3 = {'barcode': '123', 'pid': None}
        case_4 = {'barcode': None, 'pid': None}

        self.assertTrue(Util.valid_id_dict(case_1))
        self.assertTrue(Util.valid_id_dict(case_2))
        self.assertFalse(Util.valid_id_dict(case_3))
        self.assertFalse(Util.valid_id_dict(case_4))

    def test_get_brand_obj_new_brand(self):
        """ If brand doesn't exist in db, insert new row and return it """
        res = Util.get_brand_obj('brandA')
        row = Brands.objects.all()
        self.assertEqual(len(row), 1) # Assert new db insertion
        self.assertEqual(row[0].brand, 'brandA')

    def test_get_brand_obj_existing_brand(self):
        """ If brand exists in db, return Brand obj """
        brand = Brands(brand='brandA')
        brand.save()

        row = Brands.objects.all()
        self.assertEqual(len(row), 1) # Assert no new db insertion
        self.assertEqual(row[0], brand)

    def test_prepend_dict_keys(self):
        """ 
        Should prepend store name to price dict keys to match model field 
        """
        price_dict = {
            'base_price': None,
            'sale_price': None,
            'offer_price': None,
            'offer_text': None
        }
        e_res = {
            'tesco_base_price': None,
            'tesco_sale_price': None,
            'tesco_offer_price': None,
            'tesco_offer_text': None
        }
        res = Util.prepend_dict_keys(price_dict, 'tesco')
        self.assertEqual(res, e_res)


class TestScrapeIds(TestCase):
    mock_options = {
        'type': None,
        'stores': None,
        'live': False,
        'exclusive': None,
        'exclude': None
    }
    
    
    @patch('scrape.management.commands.scrape.fps.scrape_ids')
    def test_scrape_ids_integration(self, mock_scrape_ids): 
        # Arrange
        mock_id_dicts = [
            # Mock of yield results
            [{'barcode': '1', 'pid': '11'}, {'barcode': '2', 'pid': '22'}],
            [{'barcode': '3', 'pid': '33'}, {'barcode': '4', 'pid': '44'}],
            [{'barcode': '5', 'pid': '55'}, {'barcode': '6', 'pid': '66'}]
        ]
        mock_scrape_ids.return_value = mock_id_dicts

        # Act
        call_command('scrape', 'id', '-s=tesco')

        # Assert
        res = ProductInfo.objects.all()
        self.assertEqual(len(res), 6)


    def test_update_id_case_1(self):
        """ New products should result in new db rows """
        # Arrange
        options = self.mock_options
        options.update({'type': ['id']}) # manage.py scrape id
        handler = ScrapeHandler(**options) 
        new_product = {'barcode': '1', 'pid': '11'}

        # Act
        handler._update_ids(new_product, 'tesco')

        # Assert
        row = ProductInfo.objects.all()
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0].barcode, '1')
        self.assertEqual(row[0].tesco, '11')
    
    def test_update_id_case_2(self):
        """ Existing products should be updated """
        options = self.mock_options
        options.update({'type': ['id']}) # manage.py scrape id
        handler = ScrapeHandler(**options)

        existing_product = {'barcode': '1', 'pid': '11'}
        ProductInfo.objects.create(barcode=1)
        
        handler._update_ids(existing_product, 'tesco')

        row = ProductInfo.objects.all()
        self.assertEqual(len(row), 1)
        self.assertEqual(row[0].barcode, '1')
        self.assertEqual(row[0].tesco, '11')

    def test_update_id_case_3(self):
        """ If id_dict has no pid value, no db actions should be taken """
        options = self.mock_options
        options.update({'type': ['id']}) # manage.py scrape id
        handler = ScrapeHandler(**options)

        id_dict = {'barcode': '1', 'pid': None}
        handler._update_ids(id_dict, 'tesco')

        row = ProductInfo.objects.all()
        self.assertEqual(len(row), 0)


class TestScrapeInfo(TestCase):
    mock_options = {
        'type': None,
        'stores': None,
        'live': False,
        'exclusive': None,
        'exclude': None
    }

    mock_info_dict = {'description': 'b',
                      'brand': Brands.objects.create(brand='brandB'),
                      'qty':{'qty': 2,
                             'num_of_units': 2,
                             'total_qty': 2,
                             'unit_of_measurement': 'b'},
                      'nutrition': {'header': 'b',
                                    'kcal': 2,
                                    'fat': 2,
                                    'carb': 2,
                                    'protein': 2},
                      'price': {'base_price': 2,
                                'sale_price': 2,
                                'offer_price': 2,
                                'offer_text': 'b'}}


    @patch('scrape.management.commands.scrape.fps.scrape_infos')
    def test_scrape_info_integrations(self, mock_scrape_infos):
        # Arrange (1)
        mock_product = ProductInfo.objects.create(tesco='1')
        with patch.object(ProductInfo, 'objects') as mock_ProductInfo_objects:
            mock_ProductInfo_objects.filter.return_value = [mock_product]

            mock_info_dict = self.mock_info_dict
            mock_info_dict['brand'] = 'brandB'
            mock_scrape_infos.return_value = mock_info_dict
            
            # Act
            call_command('scrape', 'info', '-s=tesco')

        # Assert
        res = ProductInfo.objects.get(tesco='1')
        self.assertEqual(res.description, 'b')
        self.assertIsInstance(res.brand, Brands)
        self.assertEqual(res.brand.brand, 'brandB')

    def test_update_info_description(self):
        product = ProductInfo.objects.create(tesco='1')

        options = self.mock_options
        options['type'] = 'info'
        handler = ScrapeHandler(**options)
        handler._update_infos({'description': 'x'}, product, 'tesco')

        res = ProductInfo.objects.get(tesco=1)
        self.assertEqual(res.description, 'x')

    def test_update_info_brand(self):
        product = ProductInfo.objects.create(tesco='1')
        brand = Brands.objects.create(brand='brandX')

        options = self.mock_options
        options['type'] = 'info'
        handler = ScrapeHandler(**options)
        handler._update_infos({'brand': 'brandX'}, product, 'tesco')

        res = ProductInfo.objects.get(tesco=1)
        self.assertEqual(res.brand, brand)

    def test_update_info_qty(self):
        product = ProductInfo.objects.create(tesco='1')
        qty = {'qty': self.mock_info_dict['qty']}

        options = self.mock_options
        options['type'] = 'info'
        handler = ScrapeHandler(**options)
        handler._update_infos(qty, product, 'tesco')

        res = ProductInfo.objects.get(tesco=1)
        self.assertEqual(res.qty, 2)
        self.assertEqual(res.num_of_units, 2)
        self.assertEqual(res.total_qty, 2)
        self.assertEqual(res.unit_of_measurement, 'b')

    def test_update_info_nutrition(self):
        product = ProductInfo.objects.create(tesco='1')
        nutrition = {'nutrition': self.mock_info_dict['nutrition']}

        options = self.mock_options
        options['type'] = 'info'
        handler = ScrapeHandler(**options)
        handler._update_infos(nutrition, product, 'tesco')
        
        res = ProductInfo.objects.get(tesco=1)
        self.assertEqual(res.header, 'b')
        self.assertEqual(res.kcal, 2)
        self.assertEqual(res.fat, 2)
        self.assertEqual(res.carb, 2)
        self.assertEqual(res.protein, 2)

    def test_update_info_price(self):
        product = ProductInfo.objects.create(tesco='1')
        price = {'price': self.mock_info_dict['price']}

        options = self.mock_options
        options['type'] = 'info'
        handler = ScrapeHandler(**options)
        handler._update_infos(price, product, 'tesco')
        
        res = ProductInfo.objects.get(tesco=1)
        self.assertEqual(res.tesco_base_price, 2)
        self.assertEqual(res.tesco_sale_price, 2)
        self.assertEqual(res.tesco_offer_price, 2)
        self.assertEqual(res.tesco_offer_text, 'b')

    def test_update_info_does_not_overwrite_existing(self):
        """ Existing info should not be overwritten """
        # Arrange
        product_1 = {'description': 'a',
                     'brand': Brands.objects.create(brand='brandA'),
                     'qty': 1,
                     'num_of_units': 1,
                     'total_qty': 1,
                     'unit_of_measurement': 'a',
                     'header': 'a',
                     'kcal': 1,
                     'fat': 1,
                     'carb': 1,
                     'protein': 1,
                     'tesco_base_price': 1,
                     'tesco_sale_price': 1,
                     'tesco_offer_price': 1,
                     'tesco_offer_text': 'a'}
        
        # Act
        row = ProductInfo.objects.create(**product_1)
        options = self.mock_options
        options['type'] = 'info'
        handler = ScrapeHandler(**options)
        handler._update_infos(self.mock_info_dict, row, 'tesco')

        # Assert
        res = ProductInfo.objects.all()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].description, 'a')
        self.assertEqual(res[0].brand.brand, 'brandA')
        self.assertEqual(res[0].qty, 1)
        self.assertEqual(res[0].num_of_units, 1)
        self.assertEqual(res[0].total_qty, 1)
        self.assertEqual(res[0].unit_of_measurement, 'a')
        self.assertEqual(res[0].header, 'a')
        self.assertEqual(res[0].kcal, 1)
        self.assertEqual(res[0].fat, 1)
        self.assertEqual(res[0].carb, 1)
        self.assertEqual(res[0].protein, 1)
        self.assertEqual(res[0].tesco_base_price, 1)
        self.assertEqual(res[0].tesco_sale_price, 1)
        self.assertEqual(res[0].tesco_offer_price, 1)
        self.assertEqual(res[0].tesco_offer_text, 'a')


class TestLiveOption(TestCase):
    databases = ['default', 'live']

    mock_options = {
        'type': None,
        'stores': None,
        'live': False,
        'exclusive': None,
        'exclude': None
    }

    def test_update_id_with_live_option(self):
        """
        If --live option is used, all database actions should be directed to
        'live' db. Update function should update ID of existing product on 
        the live db instead of default db.
        """
        # Arrange: 
        # Instantiate ScrapeHandler with command options
        options = self.mock_options
        options.update({'type': ['id'],
                        'live': True}) # manage.py scrape id -l
        handler = ScrapeHandler(**options)

        # Insert identical product into default and live db
        product = ProductInfo(barcode=None, tesco='1')
        product.save() # Insert into default db
        product.save(using='live') # Insert into live db

        # Act: update db, specifically, update barcode field on live db
        handler._update_ids({'barcode': '11', 'pid': '1'}, 'tesco')

        # Assert that barcode field has been updated on live but not default db
        res_default = ProductInfo.objects.get(tesco='1')
        res_live = ProductInfo.objects.using('live').get(tesco='1')
        self.assertEqual(res_default.barcode, None)
        self.assertEqual(res_live.barcode, '11')

    def test_update_info_with_live_option(self):
        """
        If --live option is used, all database actions should be directed to
        'live' db. Update function should update/insert product info on the live
        db instead of default db.
        """
        options = self.mock_options
        options.update({'type': ['info'],
                        'live': True}) # manage.py scrape info -l
        handler = ScrapeHandler(**options)

        product = ProductInfo(tesco='1', description='x')
        product.save()
        product.save(using='live')

        handler._update_infos({'price':{'base_price': 11}}, product, 'tesco')

        res_default = ProductInfo.objects.get(tesco='1')
        res_live = ProductInfo.objects.using('live').get(tesco='1')
        self.assertEqual(res_default.tesco_base_price, None)
        self.assertEqual(res_live.tesco_base_price, 11)
        

    def test_a(self):
        call_command('scrape', 'info', '-s=tesco', '-l')