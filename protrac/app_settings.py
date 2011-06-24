"""
app_settings.py - Default app settings

This app does not import settings from settings.py directly, but pulls them
from this module. The use of getattr() allows settings to be overriden in the
projects settings.py module.

The general template for this module is as follows:
    SOME_SETTING = getattr(settings, 'PROTRAC_SOME_SETTING', default_value)

"""
from django.conf import settings


LINE_CATEGORY_CHOICES = getattr(settings, 'PROTRAC_LINE_CATEGORY_CHOICES',
        [
            ('A', u'Assembly'),
            ('X', u'Extrusion'),
            ('I', u'Injection'),
        ])
