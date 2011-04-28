from django.conf import settings

DEPARTMENT_CHOICES = getattr(settings, 'PROTRAC_PRODUCT_TYPE_CHOICES',
    [('ass', u'Assembly'),
     ('ext', u'Extrusion'),
     ('inj', u'Injection')])
