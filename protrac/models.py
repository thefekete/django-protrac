from django.db import models

from app_settings import DEPARTMENT_CHOICES


class Station(models.Model):
    """
    Manufacturing Stations
    """
    name = models.CharField(max_length=64, unique=True)
    #department = models.CharField(max_length=3, choices=DEPARTMENT_CHOICES)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)


class Product(models.Model):
    """
    Products
    """
    part_number = models.CharField(max_length=64, db_index=True, unique=True)
    #department = models.CharField(max_length=3, choices=DEPARTMENT_CHOICES)
    description = models.CharField(max_length=64, blank=True, null=True)
    cycle_time = models.FloatField(
        help_text='Time per unit in seconds (eg 5.73)')
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['part_number']

    def __unicode__(self):
        return unicode(self.part_number)


class Customer(models.Model):
    """
    Customers
    """
    name = models.CharField(max_length=64, db_index=True, unique=True)
    notes = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.name)


class Order(models.Model):
    """
    Orders
    """
    so_num = models.PositiveIntegerField(unique=True, blank=True, null=True,
        verbose_name='Sales Order Number')
    po_num = models.CharField(max_length=64, unique=True, blank=True,
        null=True, verbose_name='Purchase Order Number')
    customer = models.ForeignKey('Customer')
    recieved_date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-so_num']

    def __unicode__(self):
        return unicode(self.so_num)

    def order_lines(self):
        return self.orderline_set.count()


class OrderLine(models.Model):
    """
    Order Lines
    """
    order = models.ForeignKey('Order')
    product = models.ForeignKey('Product')
    qty = models.PositiveIntegerField(verbose_name='Quantity')
    notes = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return u'#%s %s x %ipcs' % (self.order, self.product, self.qty)

    @property
    def run_time(self):
        return self.qty * self.product.cycle_time


class Run(models.Model):
    """
    Production Runs
    """
    # have start only and calc end
    # run is closed when real_end and real_qty is input
    order_line = models.ForeignKey('OrderLine')
    station = models.ForeignKey('Station')
    qty = models.PositiveIntegerField()
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    real_qty = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)

    def is_closed(self):
        if self.start and self.end and self.real_qty:
            return True
        else:
            return False
    is_closed.short_description = 'Closed?'

    class Meta:
        ordering = ['position']

    def __unicode__(self):
        return "%i units %s for %s" % (self.qty,
            self.order_line.product, self.order_line.order.customer)
