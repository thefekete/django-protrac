from django.conf import settings

REFTYPE_CHOICES = getattr(settings, 'PROTRAC_REFTYPE_CHOICES',
    [('SO', u'Sales Order Number'),
     ('PO', u'Purchase Order Number'),
     ('-', u'Other')])
