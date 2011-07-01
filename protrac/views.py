import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from app_settings import LINE_CATEGORY_CHOICES
from models import ProductionLine


def admin_custom_view(request):
    now = datetime.datetime.now()
    html = ('<html><body>'
            'It is now %s, according to admin_custom_view...'
            '</body></html>' % now)
    return HttpResponse(html)


def schedule(request):
    objects = [ (cat, ProductionLine.objects.filter(category=abbr))
            for (abbr, cat) in LINE_CATEGORY_CHOICES ]
    return render_to_response('admin/protrac/schedule.html', locals(),
            context_instance=RequestContext(request))
