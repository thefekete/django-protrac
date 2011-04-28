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

class RunTest(TestCase):

    def setUp(self):
        # Products
        self.m2 = Product.objects.create(part_number='M2', type='ass',
            cycle_time=120)
        self.m1911 = Product.objects.create(part_number='M1911', type='ass',
            cycle_time=30)
        self.m16 = Product.objects.create(part_number='M16', type='ass',
            cycle_time=60)

        # Customers
        self.usmc = Customer.objects.create(name='USMC', notes='US Air Force')
        self.usaf = Customer.objects.create(name='USAF', notes='US Marine Corps')

        # Orders
        self.order1 = Order.objects.create(customer=self.usmc,
            recieved_date='2011-01-01', so_num=1001, po_num='verbal kent')
        self.order1_1 = OrderLine.objects.create(order=self.order1,
            product=self.m16, qty=10000)
        self.order1_2 = OrderLine.objects.create(order=self.order1,
            product=self.m1911, qty=1000)
        self.order1_3 = OrderLine.objects.create(order=self.order1,
            product=self.m2, qty=200)

        self.order2 = Order.objects.create(customer=self.usmc,
            recieved_date='2011-01-01', so_num=1002)
        self.order2_1 = OrderLine.objects.create(order=self.order2,
            product=self.m1911, qty=500)

        # Production Runs
        self.run1 = Run.objects.create(order_line=self.order2_1, qty=500)
        self.run2 = Run.objects.create(order_line=self.order1_2, qty=1000)

    def test_fail(self):
        print
        for run in Run.objects.all():
            print '=' * 40
            for k, v in run.__dict__.items():
                if not k.startswith('_'):
                    print "%-16s: %s" % (k, v)
