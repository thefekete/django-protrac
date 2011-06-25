from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from app_settings import LINE_CATEGORY_CHOICES
from models import Customer, Job, Product, ProductionLine, Run


##########
# Models #
##########

class ProductionLineTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(name='Bills Bakery')
        self.product = Product.objects.create(part_number='M1', cycle_time=1,
                material_wt=1)

    def test_scheduled_jobs(self):
        line1 = ProductionLine.objects.create(name='Line 1',
                category=LINE_CATEGORY_CHOICES[0][0])
        line2 = ProductionLine.objects.create(name='Line 2',
                category=LINE_CATEGORY_CHOICES[0][0])

        job_line1 = Job.objects.create(product=self.product, qty=1,
                customer=self.customer, production_line=line1)
        job_line2 = Job.objects.create(product=self.product, qty=1,
                customer=self.customer, production_line=line2)
        job_not_scheduled = Job.objects.create(product=self.product, qty=1,
                customer=self.customer)

        self.assertIn(job_line1, line1.scheduled_jobs())
        self.assertNotIn(job_line1, line2.scheduled_jobs())
        self.assertIn(job_line2, line2.scheduled_jobs())
        self.assertNotIn(job_line1, line2.scheduled_jobs())
        self.assertNotIn(job_not_scheduled, line1.scheduled_jobs())
        self.assertNotIn(job_not_scheduled, line2.scheduled_jobs())


class ProductTest(TestCase):

    def setUp(self):
        self.M2 = Product.objects.create(part_number='M2', cycle_time=492.5,
                material_wt=1.75)
        self.M16 = Product.objects.create(part_number='M16', cycle_time=0,
                material_wt=0)
        self.M1911 = Product.objects.create(part_number='M1911', cycle_time=2,
                material_wt=3)

    def test_product_duration(self):
        self.assertEqual(self.M2.duration(), timedelta(seconds=492.5))
        self.assertEqual(self.M2.duration(250), timedelta(seconds=123125.0))
        self.assertEqual(self.M16.duration(), timedelta(0))
        self.assertEqual(self.M16.duration(250), timedelta(0))

    def test_product_gross_wt(self):
        self.assertEqual(self.M2.gross_wt(), 1.75)
        self.assertEqual(self.M2.gross_wt(50), 87.5)
        self.assertEqual(self.M16.gross_wt(), 0)
        self.assertEqual(self.M16.gross_wt(50), 0)

    def test_avg_cycle_time(self):
        c = Customer.objects.create(name='cust1')

        j1 = Job.objects.create(product=self.M1911, qty=1000, customer=c)
        Run.objects.create(job=j1, operator='Bob', qty=30,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 1, 0))
        Run.objects.create(job=j1, operator='Bob', qty=65,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 2, 0))
        Run.objects.create(job=j1, operator='Bob', qty=55,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 2, 0))

        j2 = Job.objects.create(product=self.M1911, qty=1000, customer=c)
        Run.objects.create(job=j2, operator='Bob', qty=60,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 3, 0))
        Run.objects.create(job=j2, operator='Bob', qty=40,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 1, 0))
        Run.objects.create(job=j2, operator='Bob', qty=200,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 6, 0))

        self.assertEqual(self.M1911.avg_cycle_time(), timedelta(seconds=2))


class JobTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(name='cust1')
        self.line = ProductionLine.objects.create(name='line 1',
                category=LINE_CATEGORY_CHOICES[0][0])
        self.product = Product.objects.create(part_number='M1911',
                cycle_time=1, material_wt=1)

    def test_qtys(self):
        """
        Tests qty_done() and qty_remaining()

        """
        j = Job.objects.create(product=self.product, qty=1000,
                customer=self.customer)
        self.assertEqual(j.qty_done(), 0)
        self.assertEqual(j.qty_remaining(), 1000)

        Run.objects.create(job=j, qty=397, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.qty_done(), 397)
        self.assertEqual(j.qty_remaining(), 603)

        Run.objects.create(job=j, qty=603, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.qty_done(), 1000)
        self.assertEqual(j.qty_remaining(), 0)

        Run.objects.create(job=j, qty=256, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.qty_done(), 1256)
        self.assertEqual(j.qty_remaining(), -256)

    def test_weights(self):
        """
        Tests weight() and weight_remaining()

        """
        p = Product.objects.create(part_number='M855', cycle_time=1,
                material_wt=2.5)
        j = Job.objects.create(product=p, qty=1000, customer=self.customer)
        self.assertEqual(j.weight(), 2500)
        self.assertEqual(j.weight_remaining(), 2500)

        Run.objects.create(job=j, qty=500, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.weight(), 2500)
        self.assertEqual(j.weight_remaining(), 1250)

        Run.objects.create(job=j, qty=500, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.weight(), 2500)
        self.assertEqual(j.weight_remaining(), 0)

        Run.objects.create(job=j, qty=500, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.weight(), 2500)
        self.assertEqual(j.weight_remaining(), -1250)

    def test_weights_zero(self):
        """
        Tests weight() and weight_remaining() with product weight of zero

        """
        p = Product.objects.create(part_number='Weightless', cycle_time=1,
                material_wt=0)
        j = Job.objects.create(product=p, qty=1000, customer=self.customer)
        self.assertEqual(j.weight(), 0)
        self.assertEqual(j.weight_remaining(), 0)

        Run.objects.create(job=j, qty=500, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.weight(), 0)
        self.assertEqual(j.weight_remaining(), 0)

        Run.objects.create(job=j, qty=500, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.weight(), 0)
        self.assertEqual(j.weight_remaining(), 0)

        Run.objects.create(job=j, qty=500, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.weight(), 0)
        self.assertEqual(j.weight_remaining(), 0)

    def test_durations(self):
        """
        Tests duration() and duration_remaining()

        """
        p = Product.objects.create(part_number='Weightless', cycle_time=2.5,
                material_wt=1)
        j = Job.objects.create(product=p, qty=1000, customer=self.customer)
        self.assertEqual(j.duration(), timedelta(seconds=2500))
        self.assertEqual(j.duration_remaining(), timedelta(seconds=2500))

        Run.objects.create(job=j, qty=500, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.duration(), timedelta(seconds=2500))
        self.assertEqual(j.duration_remaining(), timedelta(seconds=1250))

        Run.objects.create(job=j, qty=500, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.duration(), timedelta(seconds=2500))
        self.assertEqual(j.duration_remaining(), timedelta(seconds=0))

        Run.objects.create(job=j, qty=500, start=datetime.now(),
                end=datetime.now())
        self.assertEqual(j.duration(), timedelta(seconds=2500))
        self.assertEqual(j.duration_remaining(), timedelta(seconds=-1250))

    def test_avg_cycle_time(self):
        p = Product.objects.create(part_number='M9',
                cycle_time=2, material_wt=3)
        j = Job.objects.create(product=p, qty=1000,
                customer=self.customer)
        Run.objects.create(job=j, operator='Bob', qty=60,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 3, 0))
        Run.objects.create(job=j, operator='Bob', qty=40,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 1, 0))
        Run.objects.create(job=j, operator='Bob', qty=200,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 6, 0))
        self.assertEqual(j.avg_cycle_time(), timedelta(seconds=2))

    def test_scheduled_manager_method(self):
        # TODO: Add tests for scheduled() in model manager
        pass

    def test_is_scheduled(self):
        j = Job.objects.create(product=self.product, qty=1000,
                customer=self.customer, pk=0)
        self.assertEqual(Job.objects.get(pk=0).is_scheduled(), False)

        j.production_line = self.line
        j.save()
        self.assertEqual(Job.objects.get(pk=0).is_scheduled(), True)

        j.void = True
        j.save()
        self.assertEqual(Job.objects.get(pk=0).is_scheduled(), False)
        j.void = False
        j.save()
        self.assertEqual(Job.objects.get(pk=0).is_scheduled(), True)

        Run.objects.create(job=j, start=datetime.now(), end=datetime.now(),
                operator='Johnny', qty=999)
        self.assertEqual(Job.objects.get(pk=0).is_scheduled(), True)
        Run.objects.create(job=j, start=datetime.now(), end=datetime.now(),
                operator='Johnny', qty=1)
        self.assertEqual(Job.objects.get(pk=0).is_scheduled(), False)
        Run.objects.create(job=j, start=datetime.now(), end=datetime.now(),
                operator='Johnny', qty=1)
        self.assertEqual(Job.objects.get(pk=0).is_scheduled(), False)


class RunTest(TestCase):

    def setUp(self):
        self.c = Customer.objects.create(name='cust1')
        self.p = Product.objects.create(part_number='M1911', cycle_time=2,
                material_wt=3)
        self.j = Job.objects.create(product=self.p, qty=1000, customer=self.c)

    def test_methods(self):
        # FIXME: Test methods individually
        # run of 100 parts over 3 minutes
        r = Run.objects.create(job=self.j, operator='Bob', qty=100,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 3, 0))
        self.assertEqual(r.weight(), 300) # 100ea * 3lbs
        self.assertEqual(r.cycle_time(), timedelta(seconds=1.8)) # 180s / 100ea

    def test_weight(self):
        pass

    def test_duration(self):
        pass

    def test_cycle_time(self):
        pass


#########
# Views #
#########

class JobScheduleViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('user', 'a@b.com', 'password')
        self.user.is_staff = True
        self.user.save()

    def test_job_schedule_view_no_login(self):
        # this redirects to a login view
        response = self.client.get(reverse('admin:schedule'))
        # make sure we got a login page
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated())
        self.assertTemplateUsed(response, 'admin/login.html')

    def test_job_schedule_view_login(self):
        self.assertTrue(self.client.login(username='user',
                password='password'))
        response = self.client.get(reverse('admin:schedule'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertTemplateNotUsed(response, 'admin/login.html')
        self.assertTemplateUsed(response, 'admin/protrac/schedule.html')

    def test_job_schedule_view(self):
        # Set up the test DB for the view
        cust = Customer.objects.create(name='Bills Bakery')
        prod = Product.objects.create(part_number='M1911', cycle_time=2,
                material_wt=3)

        for abbr, cat in LINE_CATEGORY_CHOICES:
            # make 3 production lines for each line category
            for x in range(3):
                p = ProductionLine.objects.create(
                        name='%s line %i' % (cat, x),
                        category=abbr)
                for y in range(5):
                    # put 5 jobs in each lines schedule
                    Job.objects.create(product=prod, qty=1000, customer=cust,
                            production_line=p, priority=((1 + y) * 10))

        self.assertTrue(self.client.login(username='user',
                password='password'))
        response = self.client.get(reverse('admin:schedule'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertTemplateNotUsed(response, 'admin/login.html')
        self.assertTemplateUsed(response, 'admin/protrac/schedule.html')

        # TODO: Test view context and possibly content
