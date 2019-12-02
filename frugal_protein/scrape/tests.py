from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from scrape.management.commands.scrape import Command

# Notes on call_command:
#   named args can be passed into call_command as kwargs but these kwargs are 
#   passed to the command without triggering the argument parser, and thus, 
#   may not undergo argument parser validations. Therefore, pass named args as 
#   positional args.

class ScrapeCommandTest(TestCase):
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