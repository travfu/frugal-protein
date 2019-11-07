from decimal import Decimal
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from django.urls import reverse

from calculator.forms import ProteinCalcInput

class TestCalculator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.url = reverse('protein_calculator')
        cls.data = {
                'price_value': 10,
                'qty_value': 100.0,
                'qty_unit': 'g',
                'protein_value': 20,
                'protein_per_value': 100,
                'protein_per_unit': 'g'
        }
        cls.response = cls.client.post(cls.url, cls.data)

    def test_url_dispatcher(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_get_request_returns_form_in_context(self):
        response = self.client.get(self.url)
        self.assertIsNotNone(response.context.get('form'))

    def test_valid_post_request_returns_relevant_data_in_context(self):
        """ 
        Post request with valid form data should return
            - form class
            - calculated price per unit
            - calculated price per 10g protein
        """
        self.assertIsNotNone(self.response.context)
        self.assertIsNotNone(self.response.context.get('form'))
        self.assertIsNotNone(self.response.context.get('unit_price'))
        self.assertIsNotNone(self.response.context.get('protein_price'))

    def test_invalid_post_request_returns_relevant_data_in_context(self):
        """
        Post request with invalid form data should return
            - form class
        """
        invalid_data = self.data.copy()
        invalid_data['price_value'] = 'not a digit'
        response = self.client.post(self.url, invalid_data)
        self.assertIsNotNone(response.context)
        self.assertIsNotNone(response.context.get('form'))
        self.assertIsNone(response.context.get('unit_price'))
        self.assertIsNone(response.context.get('protein_price'))

    def test_standardise_clean_data(self):
        """ 
        Form instance should standardise data as part of the data cleaning
        process. Standardising data involves converting relevant form field data
        to represent either kg, litre, or unit
        """
        form = ProteinCalcInput(self.data)     
        form.is_valid() # execute cleaning process
        data = form.cleaned_data

        # 100g should be standardised to 0.1kg
        e_qty_value = Decimal(0.1).quantize(data['qty_value'])
        self.assertEqual(data['qty_value'], e_qty_value)
        self.assertEqual(data['qty_unit'], 'kg')

        # 20g protein per 100g should be 20g protein per 0.1kg
        e_protein_value = Decimal(20).quantize(data['protein_value'])
        e_protein_per_value = Decimal(0.1).quantize(data['protein_per_value'])
        self.assertEqual(data['protein_value'], e_protein_value)
        self.assertEqual(data['protein_per_value'], e_protein_per_value)
        self.assertEqual(data['protein_per_unit'], 'kg') 

    def test_calc_unit_price(self):
        unit_price = self.response.context.get('unit_price')
        e_unit_price = Decimal(100)
        self.assertEqual(unit_price, e_unit_price)

    def test_calc_protein_price(self):
        protein_price = self.response.context.get('protein_price')
        e_protein_price = Decimal(5).quantize(protein_price)
        self.assertEqual(protein_price, e_protein_price)


class TestCalculatorLiveServer(StaticLiveServerTestCase):
    """ https://docs.djangoproject.com/en/2.2/topics/testing/tools/#liveservertestcase """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
        cls.url = cls.live_server_url + reverse('protein_calculator')
        
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def test_form_is_displayed(self):
        """ Selenium will raise a NoSuchElementException if a form element not found """
        self.selenium.get(self.url)
        try:
            price_value = self.selenium.find_element_by_name('price_value')
            qty_value = self.selenium.find_element_by_name('qty_value')
            qty_unit = self.selenium.find_element_by_name('qty_unit')
            protein_value = self.selenium.find_element_by_name('protein_value')
            protein_per_value = self.selenium.find_element_by_name('protein_per_value')
            protein_per_unit = self.selenium.find_element_by_name('protein_per_unit')
        except NoSuchElementException as e:
            self.fail(e)