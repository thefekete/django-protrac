from django.conf import settings

PRODUCTION_LINE_CHOICES = getattr(settings, 'PROTRAC_PRODUCTION_LINE_CHOICES',
    [('Assembly', (
        ('A1', u'Assembly Line 1'),
        ('A2', u'Assembly Line 2'),
        ('A3', u'Assembly Line 3'))),
     ('Extrusion', (
        ('X1', u'Extrusion Line 1'),
        ('X2', u'Extrusion Line 2'))),
     ('Injection', (
        ('I1', u'Injection Line 1'),
        ('I2', u'Injection Line 2'),
        ('I3', u'Injection Line 3'),
        ('I4', u'Injection Line 4'))),
    ])

DEPT_CHOICES = getattr(settings, 'PROTRAC_DEPT_CHOICES',
        [ (x[0] ,x[0]) for x in PRODUCTION_LINE_CHOICES ])
