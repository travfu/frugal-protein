from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase, Client
from django.urls import reverse
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

class TestCalculator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.url = reverse('protein_calculator')

    def test_url_dispatcher(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_form_in_context_in_get_response(self):
        response = self.client.get(self.url)
        self.assertIsNotNone(response.context.get('form'))

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