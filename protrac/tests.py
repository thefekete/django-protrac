"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import *


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class CustomerTest(TestCase):
    fixtures = ['test']
    
    def test_pooper_(self):
        self.c1 = Customer.objects.get(id=1)
        self.assertEqual(self.c1.name, 'pooper')
