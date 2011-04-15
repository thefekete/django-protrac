from django.db import models

# Create your models here.

class Product(models.Model):
    """
    Products
    """
    part_number = models.CharField(max_length=64, db_index=True, unique=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    unit_time = models.FloatField(
        help_text='Time per unit in seconds (eg 5.73)')
    notes = models.TextField()


class Customer(models.Model):
    """
    Customers
    """
    name = models.CharField(max_length=64, db_index=True, unique=True)
    notes = models.TextField(blank=True, null=True)


class Order(models.Model):
    """
    Orders
    """
    customer = models.ForeignKey('Customer', related_name='orders')
    recieved_date = models.DateField()
    due_date = models.DateField(blank=True, null=True)
    so_num = models.PositiveIntegerField(unique=True,
        verbose_name='Sales Order Number')
    po_num = models.CharField(max_length=64, unique=True,
        verbose_name='Purchase Order Number')
    notes = models.TextField(blank=True, null=True)


class Job(models.Model):
    """
    Jobs
    """
    id = models.AutoField(primary_key=True, verbose_name='Job Number')
    product = models.ForeignKey('Product', related_name='jobs')
    qty = models.PositiveIntegerField(verbose_name='Quantity')
    customer = models.ForeignKey('Customer')
    notes = models.TextField(blank=True, null=True)

    @property
    def run_time(self):
        return self.qty * self.product.unit_time


class Run(models.Model):
    """
    Production Runs
    """
    # Need to schedule runs
    # have start only and calc end
    # run is closed when real_end and real_qty is input
    job = models.ForeignKey('Job', related_name='runs')
    start = models.DateTimeField()
    end = models.DateTimeField()
    qty = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)

    @property
    def time_spent(self):
        td = self.end - self.start
        return ((td.microseconds + 
            float(td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)

    @property
    def real_unit_time(self):
        return self.time_spent / self.qty
