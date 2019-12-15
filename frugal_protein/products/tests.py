from django.test import TestCase

from .helper.price_calc import Calc

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
        protein = 25
        qty = 100
        uom = 'g'
        
        res = Calc.price_per_protein(price_per_unit, protein, qty, uom)
        self.assertEqual(str(res), '0.04')

    def test_unit_price_case_1(self):
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