from django.test import TestCase
from datetime import datetime, timedelta
from models import Customer, Job, Product, Run, Schedule


# class SimpleTest(TestCase):
# 
#     #fixtures = ['testfixture']
# 
#     def test_basic_addition(self):
#         """
#         Tests that 1 + 1 always equals 2.
#         """
#         self.assertEqual(1 + 1, 2)


class CustomerTest(TestCase):
    # this is kinda retarded, but we'll do it anyways...
    def test_customer(self):
        c = Customer.objects.create(name='ABC Widgets')
        self.assertEqual(c.name, 'ABC Widgets')


class ProductTest(TestCase):

    def test_product(self):
        p = Product.objects.create(part_number='M2', department='Assembly',
                cycle_time=492.5, material_wt=1.75)
        self.assertEqual(unicode(p), 'M2')
        self.assertEqual(p.duration(), timedelta(seconds=492.5))
        self.assertEqual(p.duration(25), timedelta(seconds=492.5*25))
        self.assertEqual(p.gross_wt(), 1.75)
        self.assertEqual(p.gross_wt(50), 1.75*50)

        p.material_wt = 0
        p.cycle_time = 0
        p.save()
        self.assertEqual(unicode(p), 'M2')
        self.assertEqual(p.duration(), timedelta(seconds=0))
        self.assertEqual(p.duration(25), timedelta(seconds=0))
        self.assertEqual(p.gross_wt(), 0)
        self.assertEqual(p.gross_wt(50), 0)


class JobTest(TestCase):

    def setUp(self):
        self.c = Customer.objects.create(name='cust1')
        self.p = Product.objects.create(department='Injection',
                part_number='M1911', cycle_time=2, material_wt=3)

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
        self.p0 = Product.objects.create(department='Injection',
                part_number='M16', cycle_time=2, material_wt=0)
        j0 = Job.objects.create(product=self.p0, qty=1000, customer=self.c)
        assert_methods(j0, (0, 1000, 0, 0, timedelta(seconds=2000),
            timedelta(seconds=2000)))

    def test_is_scheduled(self):
        j = Job.objects.create(product=self.p, qty=1000, customer=self.c, pk=0)
        self.assertEqual(Job.objects.get(pk=0).is_scheduled(), False)

        j.production_line = 'I1'
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
            Job.objects.create(production_line='I1', product=self.p, qty=1000,
                    customer=self.c, pk=pk)
            self.assertEqual(Job.objects.get(pk=pk).priority, 0)

        update_priority(2, 8)
        update_priority(3, 15)
        assert_priority((0, 0, 10, 20, 0))

        update_priority(4, 15)
        assert_priority((0, 0, 10, 30, 20))

        update_priority(2, 32)
        assert_priority((0, 0, 30, 20, 10))


class RunTest(TestCase):

    def setUp(self):
        self.c = Customer.objects.create(name='cust1')
        self.p = Product.objects.create(department='Injection',
                part_number='M1911', cycle_time=2, material_wt=3)
        self.j = Job.objects.create(product=self.p, qty=1000, customer=self.c)

    def test_methods(self):
        # run of 100 parts over 3 minutes
        r = Run.objects.create(job=self.j, operator='Bob', qty=100,
                start=datetime(2000, 1, 1, 0, 0, 0),
                end=datetime(2000, 1, 1, 0, 3, 0))
        self.assertEqual(r.weight(), 300) # 100ea * 3lbs
        self.assertEqual(r.cycle_time(), timedelta(seconds=1.8)) # 180s / 100ea


class ScheduleTest(TestCase):
    # TODO Add tests for schedule proxy
    pass
