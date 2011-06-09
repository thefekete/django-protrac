from datetime import timedelta

from django.db import models

from app_settings import DEPT_CHOICES
from app_settings import PRODUCTION_LINE_CHOICES


# TODO Add aggregate average of cycle time to Job and Product


###################
# ABSTRACT MODELS #
###################

class TimestampModel(models.Model):
    """
    Abstract Model Class for timestamped models
    """
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    mtime = models.DateTimeField(auto_now=True, verbose_name='Modified')

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
        return self.material_wt * qty


class Job(TimestampModel):
    """
    Bob Loblaw Job Log

    Jobs represent individual line items from POs or WOs. Their priority
    represents the order in which production resources should be allocated.
    """
    production_line = models.CharField(max_length=2,
        choices=PRODUCTION_LINE_CHOICES, blank=True, null=True, db_index=True,
        help_text='You can edit these choices in settings.py')
    product = models.ForeignKey('Product')
    qty = models.PositiveIntegerField()
    customer = models.ForeignKey('Customer')
    refs = models.CharField(max_length=128, verbose_name='References',
            help_text='Comma Separated List')
    due_date = models.DateField(blank=True, null=True)
    priority = models.PositiveIntegerField(default=0, db_index=True)
    suspended = models.CharField(max_length=32, blank=True, null=True,
            help_text='Give reason for suspension, or blank for not suspended')
    void = models.BooleanField(default=False, db_index=True)

    class Meta:
        pass

    def __unicode__(self):
        return unicode(self.id).zfill(3)

    def save(self, *args, **kwargs):
        super(Job, self).save(*args, **kwargs) # Call the "real" save()
        self.prioritize() # space priority values evenly again

    @classmethod
    def prioritize(cls):
        """
        Re-assigns priority values to be 10 apart for easy ordering by hand
        """
        for i, o in enumerate(
                cls.objects.filter(priority__gt=0).order_by('priority')):
            o.priority = (i + 1) * 10
            super(Job, o).save() # Call the "real" save()

    def is_scheduled(self):
        return self.id in [ s.id for s in Schedule.objects.all() ]
        # Here's the original method, the new one is slower but less
        # complicated.
        #if (self.production_line is not None
        #    and self.qty_remaining() > 0
        #    and self.void is not True):
        #    return True
        #else:
        #    return False

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

    Runs represent an actual production run towords a given Job.
    """
    job = models.ForeignKey('Job', db_index=True)
    qty = models.PositiveIntegerField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    operator = models.CharField(max_length=32)

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
        # use the database to filter on void and production_line, but check
        # each for qty_remaining.
        return Job.objects.filter(id__in=(
            x.id for x in Job.objects.filter(void=False).filter(
                production_line__isnull=False)
            if x.qty_remaining() > 0))

class Schedule(Job):
    """
    Scheduled Jobs Proxy

    Filters Jobs to show only "scheduled jobs". I.E. those that are not void,
    have an assigned production line, and have a quantity remaining to be
    produced (duh). This is accomplished with the ScheduleManager model
    manager above.
    """

    objects = ScheduleManager()

    class Meta:
        proxy = True
        verbose_name = 'Scheduled Job'
        verbose_name_plural = 'Job Schedule'
