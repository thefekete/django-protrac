from django.conf import settings

# Example
# SOME_SETTING = getattr(settings, 'PROTRAC_SOME_SETTING', default_value)

LINE_CATEGORY_CHOICES = getattr(settings, 'PROTRAC_LINE_CATEGORY_CHOICES',
        [
            ('A', u'Assembly'),
            ('X', u'Extrusion'),
            ('I', u'Injection'),
        ])
