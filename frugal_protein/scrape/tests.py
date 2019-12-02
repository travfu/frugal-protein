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
