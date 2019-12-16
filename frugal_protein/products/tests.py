from django.test import TestCase

from .forms import ProductSearchForm
from .helper.price_calc import Calc
from .models import ProductInfo, Brands
from .templatetags import products_filters as filters

class TestCalculations(TestCase):
    calc = Calc()
    
    def test_std_unit_multiplier_case_1(self):
        qty = 100
        uom = 'g'
        res = self.calc.std_unit_multiplier(qty, uom)
        e_res = 10
        self.assertEqual(res, e_res)
    
    def test_std_unit_multiplier_case_2(self):
        qty = 50
        uom = 'ml'
        res = self.calc.std_unit_multiplier(qty, uom)
        e_res = 20
        self.assertEqual(res, e_res)

    def test_std_unit_multiplier_case_3(self):
        qty = 10
        uom = 'kg'
        res = self.calc.std_unit_multiplier(qty, uom)
        e_res = 0.1
        self.assertEqual(res, e_res)

    def test_std_unit_multiplier_case_4(self):
        qty = 1
        uom = 'SNGL'
        res = self.calc.std_unit_multiplier(qty, uom)
        e_res = 1
        self.assertEqual(res, e_res)

    def test_price_per_protein_case_1(self):
        price_per_unit = 10  # per kg/litre/unit
        protein = 25  # 25g protein per 100g
        qty = 100
        uom = 'g'
        
        res = Calc.price_per_protein(price_per_unit, protein, qty, uom)
        self.assertEqual(str(res), '0.04')

    def test_price_per_protein_case_2(self):
        price_per_unit = 10  # per kg/litre/unit
        protein = 25  # 25g protein per 1kg
        qty = 1
        uom = 'kg'
        
        res = Calc.price_per_protein(price_per_unit, protein, qty, uom)
        self.assertEqual(str(res), '0.4')

    def test_unit_price(self):
        price = 10
        total_qty = 100
        res = Calc.unit_price(price, total_qty)
        self.assertEqual(res, 0.1)

    def test_unit_price_empty_value_behaviour(self):
        """ If any input equates to False (ie. None and 0), return None """
        res_1 = Calc.unit_price(None, 100)
        res_2 = Calc.unit_price(10, None)
        res_3 = Calc.unit_price(0, 100)
        res_4 = Calc.unit_price(10, 0)
        self.assertIsNone(res_1)
        self.assertIsNone(res_2)
        self.assertIsNone(res_3)
        self.assertIsNone(res_4)


class TestFilters(TestCase):
    def test_formatprice_case_1(self):
        res = filters.formatprice(10)
        self.assertEqual(res, '£10.00')

    def test_formatprice_case_2(self):
        res = filters.formatprice(10.5)
        self.assertEqual(res, '£10.50')

    def test_formatprice_case_3(self):
        res = filters.formatprice('10.75')
        self.assertEqual(res, '£10.75')

    def test_formatprice_case_4(self):
        res = filters.formatprice('word')
        self.assertEqual(res, 'word')

    def test_formatprice_case_4(self):
        res = filters.formatprice(None)
        self.assertEqual(res, '')

    def test_formatuom_case_1(self):
        res = filters.formatuom('sngl')
        self.assertEqual(res, 'item')

    def test_formatuom_case_2(self):
        res = filters.formatuom('l')
        self.assertEqual(res, 'litre')

    def test_formatuom_case_3(self):
        res = filters.formatuom(None)
        self.assertEqual(res, None)

    def test_formatuom_case_4(self):
        """ Should be case-insensitive to input arg """
        res = filters.formatuom('SNGL')
        self.assertEqual(res, 'item')

    def test_formatuom_case_5(self):
        res = filters.formatuom('kg')
        self.assertEqual(res, 'kg')


class TestForms(TestCase):
    # forms.py

    # Note that ProductSearchForm is designed so that a client makes a query for
    # product(s) via a GET request and the query values are passed into as 
    # initial args when instantiating the form. The form then generated a list
    # of brands and stores associated with products returned by the search 
    # query. This way, the query persists in the search bar but also, the 
    # dropdown options for brand and store will dynamically change depening on 
    # the search query.

    @classmethod
    def setUpTestData(cls):
        cls.brandA = Brands.objects.create(brand='brand A')
        cls.brandB = Brands.objects.create(brand='brand B')
        cls.brandC = Brands.objects.create(brand='brand C')

    def test_brand_options_behaviour(self):
        """ 
        Brand choicefield should return a dynamic list of brands that is
        dependent on the search query
        """
        # 3 products, 3 brands
        ProductInfo.objects.create(description='turkey A', 
                                   brand_id=self.brandA.brand_id)
        ProductInfo.objects.create(description='turkey B',
                                   brand_id=self.brandB.brand_id)
        ProductInfo.objects.create(description='chicken',
                                   brand_id=self.brandC.brand_id)
        
        # Mock search query
        mock_query = {'initial': {'search': 'turkey'}}
        bound_form = ProductSearchForm(**mock_query)
        brand_choices = bound_form.fields['brand'].choices

        # Assert brands associated with search query is found in dropdown 
        # options (ie. brand A & B, but not C)
        e_1 = (self.brandA.brand_id, self.brandA.brand.title())
        e_2 = (self.brandB.brand_id, self.brandB.brand.title())
        e_3 = (self.brandC.brand_id, self.brandC.brand.title())
        self.assertIn(e_1, brand_choices)
        self.assertIn(e_2, brand_choices)
        self.assertNotIn(e_3, brand_choices)

    def test_brand_options_uses_full_txt_search(self):
        """         
        Brands listed in dropdown should be should match the products returned
        by get_queryset in Views, which uses psql full text search. Thus,
        the brand field should also utilise full text search
        """
        # Standard PSQL query for 'turkey mince' will not match 'turkey xxx 
        # mince', but full text search will.
        ProductInfo.objects.create(description='turkey xxx mince', 
                                   brand_id=self.brandA.brand_id)
        mock_query = {'initial': {'search': 'turkey mince'}}
        bound_form = ProductSearchForm(**mock_query)
        brand_choices = bound_form.fields['brand'].choices
        
        e_1 = (self.brandA.brand_id, self.brandA.brand.title())
        e_2 = (self.brandB.brand_id, self.brandB.brand.title())
        self.assertIn(e_1, brand_choices)
        self.assertNotIn(e_2, brand_choices)

    def test_store_options_behaviour(self):
        """ 
        Store choicefield should return a list of all stores, independently of
        product query
        """
        ProductInfo.objects.create(description='turkey', tesco='123',
                                   iceland=None)
        mock_query = {'initial': {'search': 'turkey'}}
        bound_form = ProductSearchForm(**mock_query)
        store_choices = bound_form.fields['store'].choices

        self.assertIn(('tesco', 'Tesco'), store_choices)
        self.assertIn(('iceland', 'Iceland'), store_choices)