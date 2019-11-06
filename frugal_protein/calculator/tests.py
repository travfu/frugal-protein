from django.test import TestCase, Client
from django.urls import reverse

class TestCalculator(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('protein_calculator')

    def test_url_dispatcher(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)