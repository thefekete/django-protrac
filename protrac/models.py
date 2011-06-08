from datetime import timedelta

from django.db import models

from app_settings import DEPT_CHOICES
from app_settings import PRODUCTION_LINE_CHOICES


###################
# ABSTRACT MODELS #
###################

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


##################
# REGULAR MODELS #
##################

class Customer(models.Model):
    """
    Customers
    """
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        # abstract = True
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Product(TimestampModel):
    """
    Products
    """
    department = models.CharField(max_length=64, choices=DEPT_CHOICES,
        help_text='You can edit these choices in settings.py')
    part_number = models.CharField(max_length=64, db_index=True, unique=True)
    description = models.TextField(blank=True, null=True)
    setup = models.TextField(blank=True, null=True)
    cycle_time = models.FloatField(
        help_text='Time per unit in seconds (eg 5.73)')
    material_wt = models.FloatField(default=0, verbose_name='Material Weight',
        help_text='Material Weight per Unit in Pounds')

    class Meta:
        ordering = ['part_number']

    def __unicode__(self):
        return unicode(self.part_number)

    def duration(self, qty=1):
        return timedelta(seconds=self.cycle_time) * qty

    def gross_wt(self, qty=1):
        try:
            return self.material_wt * qty
        except TypeError:
            return None


class Job(TimestampModel):
    """
    Bob Loblaw Job Log

    Jobs represent individual line items from POs or WOs. Their priority
    represents the order in which production resources should be allocated.
    """
    production_line = models.CharField(max_length=2,
        choices=PRODUCTION_LINE_CHOICES, blank=True, null=True,
        help_text='You can edit these choices in settings.py')
    product = models.ForeignKey('Product')
    qty = models.PositiveIntegerField()
    customer = models.ForeignKey('Customer')
    refs = models.CharField(max_length=128, blank=True, null=True,
        verbose_name='References', help_text='Comma Separated List')
    due_date = models.DateField(blank=True, null=True)
    priority = models.PositiveIntegerField(default=0)
    suspended = models.CharField(max_length=32, blank=True, null=True)
    void = models.BooleanField(default=False)

    class Meta:
        pass

    def __unicode__(self):
        return unicode(self.id).zfill(3)

    def save(self, *args, **kwargs):
        super(Job, self).save(*args, **kwargs) # Call the "real" save()
        self.prioritize()

    @classmethod
    def prioritize(cls):
        for i, o in enumerate(
                cls.objects.filter(priority__gt=0).order_by('priority')):
            o.priority = (i + 1) * 10
            super(Job, o).save() # Call the "real" save()

    def is_scheduled(self):
        if (self.production_line is not None
            and self.qty_remaining() > 0
            and self.void is not True):
            return True
        else:
            return False

    def qty_done(self):
        qty = self.run_set.aggregate(models.Sum('qty'))['qty__sum']
        if qty is None:
            return 0
        else:
            return int(qty)

    def qty_remaining(self):
        return self.qty - self.qty_done()

    def weight(self):
        return self.product.gross_wt(self.qty)

    def weight_remaining(self):
        return self.product.gross_wt(self.qty_remaining())

    def duration(self):
        return self.product.duration(self.qty)

    def duration_remaining(self):
        return self.product.duration(self.qty_remaining())


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
        return unicode(self.id).zfill(3)

    def weight(self):
        return self.job.product.gross_wt(self.qty)

    def cycle_time(self):
        return (self.end - self.start) / self.qty


################
# PROXY MODELS #
################

class ScheduleManager(models.Manager):
    def get_query_set(self):
        # We want to filter just scheduled jobs, i.e not void, sent to
        # production line and with qty remaining.
        #
        # Job.is_scheduled() does all this, but we can pre-filter on void and
        # production line in the database, so we will.
        return Job.objects.filter(id__in=(
            x.id for x in Job.objects.filter(void=False).filter(
                production_line__isnull=False)
            if x.is_scheduled() == True ))

class Schedule(Job):
    """
    Scheduled Jobs Proxy
    """

    objects = ScheduleManager()

    class Meta:
        proxy = True
        verbose_name = 'Scheduled Job'
        verbose_name_plural = 'Job Schedule'
