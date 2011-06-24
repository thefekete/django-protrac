"""
apptest_urls.py - urlconf for standalone app testing with app-test-runner

To run the tests:
    app-test-runner protrac -s apptest_settings.py

"""
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
)
