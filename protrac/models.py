from datetime import timedelta

from django.db import models

from app_settings import REFTYPE_CHOICES


class NameModel(models.Model):
    """
    Abstract Model Class for single field ('name') models
    """
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)


class TimestampModel(models.Model):
    """
    Abstract Model Class for timestamped models
    """
    ctime = models.DateTimeField(auto_now_add=True,
        help_text='Creation Timestamp')
    mtime = models.DateTimeField(auto_now=True,
        help_text='Modified Timestamp')

    class Meta:
        abstract = True


class Customer(NameModel):
    """
    Customers
    """
    pass


class Department(NameModel):
    """
    Customers
    """
    pass


class Station(NameModel):
    """
    Customers
    """
    department = models.ForeignKey('Department')


class Product(TimestampModel):
    """
    Products
    """
    department = models.ForeignKey('Department')
    part_number = models.CharField(max_length=64, db_index=True, unique=True)
    description = models.TextField(blank=True, null=True)
    cycle_time = models.FloatField(
        help_text='Time per unit in seconds (eg 5.73)')
    material_wt = models.FloatField(blank=True, null=True,
        verbose_name='Material weight',
        help_text='Material Weight / Unit in Pounds')

    class Meta:
        ordering = ['part_number']

    def __unicode__(self):
        return unicode(self.part_number)

    def duration(self, qty=1):
        return timedelta(seconds=self.cycle_time) * qty

    def gross_wt(self, qty=1):
        return self.material_wt * qty


class Job(TimestampModel):
    """
    Bob Loblaw Job Log
    """
    station = models.ForeignKey('Station', blank=True, null=True)
    product = models.ForeignKey('Product')
    qty = models.PositiveIntegerField()
    customer = models.ForeignKey('Customer')
    refs = models.CharField(max_length=128, blank=True, null=True,
        help_text='Comma Separated List')
    due_date = models.DateField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)
    void = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    class Meta:
        pass

    def __unicode__(self):
        return unicode(self.id)

    def is_scheduled(self):
        if self.station is not None:
            return True
        else:
            return False

    def qty_done(self):
        qty = self.run_set.aggregate(models.Sum('qty'))['qty__sum']
        if qty is None:
            return 0
        else:
            return int(qty)

    def qty_balance(self):
        return self.qty - self.qty_done()

    def weight(self):
        return self.product.gross_wt(self.qty)

    def weight_balance(self):
        return self.product.gross_wt(self.qty_balance())

    def duration(self):
        return self.product.duration(self.qty)

    def duration_balance(self):
        return self.product.duration(self.qty_balance())


class Run(TimestampModel):
    """
    Run Log
    """
    job = models.ForeignKey('Job')
    qty = models.PositiveIntegerField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    operator = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        pass

    def __unicode__(self):
        return unicode(self.id)

    def weight(self):
        return self.job.product.weight * self.qty

    def cycle_time(self):
        return (self.end - self.start) / self.qty


class JobSchedule(Job):
    """
    Scheduled Jobs Proxy
    """

    class Meta:
        proxy = True
        verbose_name = 'Jobs > Scheduled'
        verbose_name_plural = 'Jobs > Scheduled'


class JobLog(Job):
    """
    Scheduled Jobs Proxy
    """

    class Meta:
        proxy = True
        verbose_name = 'Jobs > Log'
        verbose_name_plural = 'Jobs > Log'
