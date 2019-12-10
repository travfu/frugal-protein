from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from products.models import ProductInfo, Brands
from scrape.management.commands.scrape import Command


class TestScrapeCommand(TestCase):
    # Notes on call_command:
    #   named args can be passed into call_command as kwargs but these kwargs 
    #   are passed to the command without triggering the argument parser, and 
    #   thus, may not undergo argument parser validations. Therefore, pass 
    #   named args as positional args.

    def test_invalid_scrape_type(self):
        """ Error should be raised if an invalid arg is passed in """
        with self.assertRaises(CommandError):
            call_command('scrape', 'invalid type')
    
    def test_mutual_exclusive_arguments(self):
        """ Only one of two arguments (-a or -s) can be used for any command """
        with self.assertRaises(CommandError):
            call_command('scrape', 'id', '-a', '-s=tesco')

    def test_invalid_store_option(self):
        """ Error should be raised if unimplemented store is passed via -s """
        with self.assertRaises(CommandError):
            call_command('scrape', 'info', '-s=randomstore')

    def test_correct_handling_scrape_id(self):
        """ Passing in 'id' arg should call scrape_ids method """
        with patch.object(Command, 'scrape_ids') as mock_method:
            call_command('scrape', 'id', '-a')
            mock_method.assert_called_once()

    def test_correct_handling_scrape_info(self):
        """ Passing in 'info' arg should call scrape_infos method """
        with patch.object(Command, 'scrape_infos') as mock_method:
            call_command('scrape', 'info', '-a')
            mock_method.assert_called_once()
    
    def test_correct_handling_scrape_price(self):
        """ Passing in 'price' arg should call scrape_prices method """
        with patch.object(Command, 'scrape_prices') as mock_method:
            call_command('scrape', 'price', '-a')
            mock_method.assert_called_once()

 
class TestRowFiltering(TestCase):    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.command = Command()

        cls.desc = {'description': 'sample product'}
        cls.qty = {'qty': 1, 
                   'num_of_units': 1, 
                   'total_qty': 1, 
                   'unit_of_measurement': 'g'}
        cls.nutr = {'header': 'per 100g', 
                    'kcal': 1, 
                    'fat': 1, 
                    'carb': 1, 
                    'protein': 1}

    
    def test_get_rows_for_info_scrape(self):
        """ Should return rows that require info scraping """
        # Arrange
        ProductInfo.objects.create(
            pid=1, tesco='1', **self.desc, **self.qty, **self.nutr
        )
        ProductInfo.objects.create(
            pid=2, tesco='2', **self.desc
        )

        # Act
        rows = self.command.get_rows_for_info_scrape('tesco')
        rows = [row.pid for row in rows]
        e_res = [2]

        # Assert
        self.assertEqual(rows, e_res)


    def test_get_rows_for_info_scrape_OR_operator(self):
        """ 
        Should return rows that have missing description OR qty OR nutrition 
        """
        ProductInfo.objects.create(
            pid=1, tesco='1', **self.desc, **self.qty
        )
        ProductInfo.objects.create(
            pid=2, tesco='2', **self.desc, **self.nutr
        )
        ProductInfo.objects.create(
            pid=3, tesco='3', **self.qty, **self.nutr
        )

        rows = self.command.get_rows_for_info_scrape('tesco')
        rows = [row.pid for row in rows]
        e_res = [1, 2, 3]

        self.assertEqual(rows, e_res)

    def test_get_rows_for_price_scrape(self):
        """ 
        Should return rows that qualify for price scraping 
        (i.e. has all info values)
        """
        # Qualifies for price scrape
        ProductInfo.objects.create(
            pid=1, tesco='1', **self.desc, **self.qty, **self.nutr
        )
        # Does not qualify for price scrape
        ProductInfo.objects.create(
            pid=2, tesco='2', **self.desc
        )

        rows = self.command.get_rows_for_price_scrape('tesco')
        rows = [row.pid for row in rows]
        e_res = [1]

        self.assertEqual(rows, e_res)

class TestScrapeInfo(TestCase):
    def test_update_info(self):
        # Arrange - Insert product without any product info into db
        product = ProductInfo.objects.create(pid=1, tesco='1')

        # Act
        info_dict = {'description': 'sample product',
                    #  'brand': 'sample brand',
                     'qty_dict': {'qty': 1, 
                                  'num_of_units': 1, 
                                  'total_qty': 1, 
                                  'unit_of_measurement': 'g'},
                     'nutrition_dict': {'header': 'per 100g', 
                                        'kcal': 1, 
                                        'fat': 1, 
                                        'carb': 1, 
                                        'protein': 1}}                    
        Command().update_info_result(info_dict, product)

        # Assert description and brand is updated
        self.assertEqual(product.description, info_dict['description'])
        
        # Assert quantity is updated
        qty = info_dict['qty_dict']
        self.assertEqual(product.qty, qty['qty'])
        self.assertEqual(product.num_of_units, qty['num_of_units'])
        self.assertEqual(product.total_qty, qty['total_qty'])
        self.assertEqual(product.num_of_units, qty['num_of_units'])
        
        # Assert nutrition is updated
        nutrition = info_dict['nutrition_dict']
        self.assertEqual(product.header, nutrition['header'])
        self.assertEqual(product.kcal, nutrition['kcal'])
        self.assertEqual(product.fat, nutrition['fat'])
        self.assertEqual(product.carb, nutrition['carb'])
        self.assertEqual(product.protein, nutrition['protein'])

    def test_update_info_does_not_overwrite_existing(self):
        """ Existing info should not be overwritten """
        product = ProductInfo.objects.create(pid=1, tesco=1, description='x')
        info_dict = {'description': 'sample product'}                    
        Command().update_info_result(info_dict, product)
        
        # Assert description is not overwritten
        self.assertEqual(product.description, 'x')

    def test_update_info_brand(self):
        """ Brand should be a reference (Foreign Key) to a brand object """
        product = ProductInfo.objects.create(pid=1, tesco=1)
        info_dict = {'brand': 'brand X'}
        Command().update_info_result(info_dict, product)

        e_res = Brands.objects.filter(brand=info_dict['brand'])
        self.assertEqual(product.brand, e_res[0]) 

    def test_get_brand_object_new_brand(self):
        """ Should insert new brand to db and return as object """        
        res = Command().get_brand_object('brand X')
        row_count = len(Brands.objects.filter(brand='brand X'))
        self.assertEqual(row_count, 1) # assert new row created
        self.assertEqual(res.brand, 'brand X')

    def test_get_brand_object_existing_brand(self):
        """ 
        Should not insert new brand but return brand object that already 
        exists in db 
        """
        Brands.objects.create(brand='brand X')
        res = Command().get_brand_object('brand X')
        row_count = len(Brands.objects.filter(brand='brand X'))
        self.assertEqual(row_count, 1) # assert no new rows created
        self.assertEqual(res.brand, 'brand X')


class TestScrapePrice(TestCase):
    @patch('scrape.management.commands.scrape.fps.scrape_infos')
    @patch.object(Command, 'get_rows_for_price_scrape')
    def test_scrape_price(self, mock_get_rows, mock_scrape_infos):
        mock_product = ProductInfo.objects.create(pid=1, tesco=1)
        mock_info_dict = {
            'price_dict': {
                'base_price': 1,
                'sale_price': 1,
                'offer_price': 1,
                'offer_text': 'offer'
            }
        }
        
        mock_get_rows.return_value = [mock_product]
        mock_scrape_infos.return_value = mock_info_dict
        Command().scrape_prices(stores=['tesco'])

        # Assert db object is updated with price data
        res = ProductInfo.objects.get(pid=1)
        self.assertEqual(res.tesco_base_price, 1)
    
    def test_prepend_dict_keys(self):
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
        res = Command().prepend_dict_keys(price_dict, 'tesco')
        self.assertEqual(res, e_res)
    

    def test_update_price_result(self):
        # Note that truncated rows (i.e. missing values) are used for testing
        # but previous queryset filtering should have filtered out such 
        # truncated rows for price scraping. 
        product = ProductInfo.objects.create(pid=1, tesco=1)
        price_dict = {
            'tesco_base_price': 1, 
            'tesco_sale_price': 2, 
            'tesco_offer_price': 3, 
            'tesco_offer_text': 'offer'
        }

        Command().update_price_result(price_dict, product)

        res = ProductInfo.objects.get(pid=1)
        self.assertEqual(res.tesco_base_price, 1)
        self.assertEqual(res.tesco_sale_price, 2)
        self.assertEqual(res.tesco_offer_price, 3)
        self.assertEqual(res.tesco_offer_text, 'offer')
    

    def test_update_price_result_overwrites(self):
        """ Existing price data should be overwritten """
        product = ProductInfo.objects.create(pid=1, tesco=1,
                                             tesco_base_price=1,
                                             tesco_sale_price=2,
                                             tesco_offer_price=3,
                                             tesco_offer_text='offer')
        price_dict = {
            'tesco_base_price': 10, 
            'tesco_sale_price': 11, 
            'tesco_offer_price': 12, 
            'tesco_offer_text': 'new offer'
        }

        Command().update_price_result(price_dict, product)

        res = ProductInfo.objects.get(pid=1)
        self.assertEqual(res.tesco_base_price, 10)
        self.assertEqual(res.tesco_sale_price, 11)
        self.assertEqual(res.tesco_offer_price, 12)
        self.assertEqual(res.tesco_offer_text, 'new offer')


class TestScrapeIds(TestCase):
    @patch('scrape.management.commands.scrape.fps.scrape_ids')
    def test_scrape_ids(self, mock_scrape_ids):   
        mock_id_dicts = [
            # Mock of yield results
            [{'barcode': '1', 'pid': '11'}, {'barcode': '2', 'pid': '22'}],
            [{'barcode': '3', 'pid': '33'}, {'barcode': '4', 'pid': '44'}],
            [{'barcode': '5', 'pid': '55'}, {'barcode': '6', 'pid': '66'}]
        ]
        mock_scrape_ids.return_value = mock_id_dicts

        Command().scrape_ids(['tesco'])

        res = ProductInfo.objects.all()
        self.assertEqual(len(res), 6)

    def test_update_id_result_case_1(self):
        """ New product; should create new row """
        id_dict = {'barcode': '1', 'pid': '100'}
        Command().update_id_result(id_dict, 'tesco')

        res = ProductInfo.objects.all()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].barcode, '1')
        self.assertEqual(res[0].tesco, '100')

    def test_update_id_result_case_2(self):
        """
        Missing pid or both barcode/pid should not insert/update row
        """
        id_dict_1 = {'barcode': '1', 'pid': None}
        id_dict_2 = {'barcode': None, 'pid': None}
        Command().update_id_result(id_dict_1, 'tesco')
        Command().update_id_result(id_dict_2, 'tesco')

        res = ProductInfo.objects.all()
        self.assertEqual(len(res), 0)

    def test_update_id_result_case_3(self):
        """ 
        Existing product with identical barcode but no store_pid - 
        should update existing row with new store_pid
        """
        ProductInfo.objects.create(barcode='1')
        id_dict = {'barcode': '1', 'pid': '100'}
        Command().update_id_result(id_dict, 'tesco')

        res = ProductInfo.objects.all()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].barcode, '1')
        self.assertEqual(res[0].tesco, '100')

    def test_update_id_result_case_4(self):
        """
        Existing product with identical store_pid but no barcode -
        should update existing row with new barcode
        """
        ProductInfo.objects.create(tesco='100')
        id_dict = {'barcode': '1', 'pid': '100'}
        Command().update_id_result(id_dict, 'tesco')

        res = ProductInfo.objects.all()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].barcode, '1')
        self.assertEqual(res[0].tesco, '100')