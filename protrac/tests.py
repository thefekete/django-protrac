from datetime import datetime, timedelta

from django.test import TestCase

from models import Customer, Job, Product, ProductionLine, Run, Schedule
from app_settings import LINE_CATEGORY_CHOICES


##########
# Models #
##########

class CustomerTest(TestCase):

    def test_customer(self):
        # Just test object creation
        c = Customer.objects.create(name='ABC Widgets')
        self.assertEqual(unicode(c), u'ABC Widgets')
        self.assertEqual(c.name, u'ABC Widgets')


class ProductionLineTest(TestCase):

    def test_model(self):
        # Just test object creation...
        pl = ProductionLine.objects.create(name='Line 1',
                category=LINE_CATEGORY_CHOICES[0][0])

        self.assertEqual(unicode(pl), u'Line 1')
        self.assertEqual(pl.name, u'Line 1')
        self.assertEqual(pl.get_category_display(),
                LINE_CATEGORY_CHOICES[0][1])


class ProductTest(TestCase):

    def setUp(self):
        self.M2 = Product.objects.create(part_number='M2', cycle_time=492.5,
                material_wt=1.75)
        self.M16 = Product.objects.create(part_number='M16', cycle_time=0,
                material_wt=0)
        self.M1911 = Product.objects.create(part_number='M1911', cycle_time=2,
                material_wt=3)

    def test_product_part_number(self):
        self.assertEqual(unicode(self.M2), u'M2')
        self.assertEqual(unicode(self.M16), u'M16')

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
        self.c = Customer.objects.create(name='cust1')
        self.pl = ProductionLine.objects.create(name='line 1', category='X')
        self.p = Product.objects.create(part_number='M1911', cycle_time=2,
                material_wt=3)

    def test_methods(self):
        methods = ('qty_done', 'qty_remaining', 'weight', 'weight_remaining',
                'duration', 'duration_remaining')

        def assert_methods(obj, vals):
            for m, v in zip(methods, vals):
                ret = getattr(obj, m)()
                try:
                    self.assertEqual(ret, v)
                except AssertionError:
                    raise AssertionError('%s[%s].%s() returned %s expected %s'
                            % (obj.__class__.__name__, obj.pk, m, ret, v))

        j = Job.objects.create(product=self.p, qty=1000, customer=self.c)

        assert_methods(j, (0, 1000, 3000, 3000, timedelta(seconds=2000),
            timedelta(seconds=2000)))

        Run.objects.create(job=j, start=datetime.now(), end=datetime.now(),
                operator='Johnny', qty=250)
        assert_methods(j, (250, 750, 3000, 2250, timedelta(seconds=2000),
            timedelta(seconds=1500)))

        Run.objects.create(job=j, start=datetime.now(), end=datetime.now(),
                operator='Johnny', qty=750)
        assert_methods(j, (1000, 0, 3000, 0, timedelta(seconds=2000),
            timedelta(seconds=0)))

        # Test product with zero weight
        self.p0 = Product.objects.create(part_number='M16', cycle_time=2,
                material_wt=0)
        j0 = Job.objects.create(product=self.p0, qty=1000, customer=self.c)
        assert_methods(j0, (0, 1000, 0, 0, timedelta(seconds=2000),
            timedelta(seconds=2000)))

    def test_is_scheduled(self):
        j = Job.objects.create(product=self.p, qty=1000, customer=self.c, pk=0)
        self.assertEqual(Job.objects.get(pk=0).is_scheduled(), False)

        j.production_line = self.pl
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

    def test_prioritize(self):
        def update_priority(pkey, priority):
            o = Job.objects.get(pk=pkey)
            o.priority = priority
            o.save()

        def assert_priority(plist):
            for pk, priority in enumerate(plist):
                self.assertEqual(Job.objects.get(pk=pk).priority, priority)

        # Create Jobs and assert that priorities start at 0
        for pk in range(5):
            Job.objects.create(production_line=self.pl, product=self.p, qty=1000,
                    customer=self.c, pk=pk)
            self.assertEqual(Job.objects.get(pk=pk).priority, 0)

        update_priority(2, 8)
        update_priority(3, 15)
        assert_priority((0, 0, 10, 20, 0))

        update_priority(4, 15)
        assert_priority((0, 0, 10, 30, 20))

        update_priority(2, 32)
        assert_priority((0, 0, 30, 20, 10))

    def test_avg_cycle_time(self):
        j = Job.objects.create(product=self.p, qty=1000, customer=self.c)
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


class RunTest(TestCase):

    def setUp(self):
        self.c = Customer.objects.create(name='cust1')
        self.p = Product.objects.create(part_number='M1911', cycle_time=2,
                material_wt=3)
        self.j = Job.objects.create(product=self.p, qty=1000, customer=self.c)

    def test_methods(self):
        # run of 100 parts over 3 minutes
        r = Run.objects.create(job=self.j, operator='Bob', qty=100,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 3, 0))
        self.assertEqual(r.weight(), 300) # 100ea * 3lbs
        self.assertEqual(r.cycle_time(), timedelta(seconds=1.8)) # 180s / 100ea


class ScheduleTest(TestCase):

    def setUp(self):
        self.c = Customer.objects.create(name='cust1')
        self.pl = ProductionLine.objects.create(name='line 1', category='X')
        self.p = Product.objects.create(part_number='M1911', cycle_time=2,
                material_wt=3)

    def test_manager(self):
        scheduled = (
                # Job 001
                Job.objects.create(product=self.p, qty=1000, customer=self.c,
                    production_line=self.pl, pk=1),
                # Job 002
                Job.objects.create(product=self.p, qty=1000, customer=self.c,
                    production_line=self.pl, pk=2),
                # Job 003
                Job.objects.create(product=self.p, qty=1000, customer=self.c,
                    suspended='No material', production_line=self.pl, pk=3),)
        Run.objects.create(job=scheduled[1], qty=999, operator='j',
                start=datetime.now(), end=datetime.now())

        not_scheduled = (
                # Job 004: no production line:
                Job.objects.create(product=self.p, qty=1000, customer=self.c,
                    pk=4),
                # Job 005: void:
                Job.objects.create(product=self.p, qty=1000, customer=self.c,
                    production_line=self.pl, void=True, pk=5),
                # Job 006: completed qty (via Run below):
                Job.objects.create(product=self.p, qty=1000, customer=self.c,
                    production_line=self.pl, pk=6),
                # Job 007: overshoot qty (via Run below):
                Job.objects.create(product=self.p, qty=1000, customer=self.c,
                    production_line=self.pl, pk=7),)
        Run.objects.create(job=not_scheduled[2], qty=1000, operator='j',
                start=datetime.now(), end=datetime.now())
        Run.objects.create(job=not_scheduled[3], qty=1001, operator='j',
                start=datetime.now(), end=datetime.now())

        job_pks = [ j.pk for j in Job.objects.all() ]
        schedule_pks = [ j.pk for j in Schedule.objects.all() ]

        for s in scheduled:
            if s.pk not in schedule_pks:
                raise AssertionError(
                        '%s should be in Schedule, but its not...' % repr(s))

        for n in not_scheduled:
            if n.pk in schedule_pks:
                raise AssertionError(
                        '%s should not be in Schedule, but it is...' % repr(n))
