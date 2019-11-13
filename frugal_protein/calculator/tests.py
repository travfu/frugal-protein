from decimal import Decimal
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
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
        self.assertIsNotNone(self.response.context.get('results'))

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
        self.assertIsNone(response.context.get('results'))

    def test_standardise_units(self):
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
        unit_price = self.response.context['results']['unit_price']
        e_unit_price = Decimal(100)
        self.assertEqual(unit_price, e_unit_price)

    def test_calc_protein_price(self):
        protein_price = self.response.context['results']['protein_price']
        e_protein_price = Decimal(5).quantize(protein_price)
        self.assertEqual(protein_price, e_protein_price)

    def test_unit_compatability(self):
        """
        Error should be raised if units are incompatible.

        An example of incompatability is a 100g product with 20g protein per 
        100ml - 100g and 100ml are incompatible. On the other hand, 1kg and 
        100g would be compatible.
        """
        def get_form_field_error(data):
            response = self.client.post(self.url, data)
            form = response.context.get('form')
            qty_unit = form.errors.get('qty_unit')
            protein_per_unit = form.errors.get('protein_per_unit')
            return (qty_unit, protein_per_unit)

        # g and kg are compatible
        data = self.data.copy()
        data['qty_unit'] = 'g'
        data['protein_per_unit'] = 'kg'
        qty_unit, protein_per_unit = get_form_field_error(data)
        self.assertIsNone(qty_unit)
        self.assertIsNone(protein_per_unit)
       
        # kg and ml are incompatible
        data['qty_unit'] = 'kg'
        data['protein_per_unit'] = 'ml'
        qty_unit, protein_per_unit = get_form_field_error(data)
        self.assertIsNotNone(qty_unit)
        self.assertIsNotNone(protein_per_unit)

class TestCalculatorLiveServer(StaticLiveServerTestCase):
    """ https://docs.djangoproject.com/en/2.2/topics/testing/tools/#liveservertestcase """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)
        cls.url = cls.live_server_url + reverse('protein_calculator')
        cls.selenium.get(cls.url)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
        
    def test_form_post(self):
        """ 
        Submitting a valid form should return calculation results
        """
        try:
            price_value = self.selenium.find_element_by_name('price_value')
            qty_value = self.selenium.find_element_by_name('qty_value')
            qty_unit = self.selenium.find_element_by_name('qty_unit')
            protein_value = self.selenium.find_element_by_name('protein_value')
            protein_per_value = self.selenium.find_element_by_name('protein_per_value')
            protein_per_unit = self.selenium.find_element_by_name('protein_per_unit')
            submit_btn = self.selenium.find_element_by_css_selector('button')
        except NoSuchElementException as e:
            self.fail(e)

        def send_keys(element, value):
            element.clear()
            element.send_keys(value)

        def select_option(element, value):
            select_element = Select(element)
            select_element.select_by_value(value)

        # Input test product: £2.00, 1.5litre, 20g protein per 100ml
        send_keys(price_value, '2')
        send_keys(qty_value, '1.5')
        select_option(qty_unit, 'l')
        send_keys(protein_value, '20')
        send_keys(protein_per_value, '100')
        select_option(protein_per_unit, 'ml')

        # Submit form
        submit_btn.click()

        # Input value should persist in form fields after submission
        try:
            price_value = self.selenium.find_element_by_name('price_value')
            qty_value = self.selenium.find_element_by_name('qty_value')
            qty_unit = self.selenium.find_element_by_name('qty_unit')
            protein_value = self.selenium.find_element_by_name('protein_value')
            protein_per_value = self.selenium.find_element_by_name('protein_per_value')
            protein_per_unit = self.selenium.find_element_by_name('protein_per_unit')
        except NoSuchElementException as e:
            self.fail(e)

        self.assertEqual(price_value.get_attribute('value'), '2')
        self.assertEqual(qty_value.get_attribute('value'), '1.5')
        self.assertEqual(qty_unit.get_attribute('value'), 'l')
        self.assertEqual(protein_value.get_attribute('value'), '20')
        self.assertEqual(protein_per_value.get_attribute('value'), '100')
        self.assertEqual(protein_per_unit.get_attribute('value'), 'ml')

        # Read results
        unit_price = self.selenium.find_element_by_id('unit_price')
        protein_price = self.selenium.find_element_by_id('protein_price')
        e_unit_price_text = 'Unit Price: £1.33/litre'
        e_protein_price_text = 'Price Per 10g Protein: £0.07'

        self.assertEqual(unit_price.text, e_unit_price_text)
        self.assertEqual(protein_price.text, e_protein_price_text)

        # Click reset button to clear form values
        try: 
            reset_btn = self.selenium.find_element_by_id('btn-reset')
        except NoSuchElementException as e:
            self.fail(e)
        reset_btn.click()

        self.assertEqual(price_value.get_attribute('value'), '')
        self.assertEqual(qty_value.get_attribute('value'), '')
        self.assertEqual(protein_value.get_attribute('value'), '')
        self.assertEqual(protein_per_value.get_attribute('value'), '')
