import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import Job


def admin_custom_view(request):
    now = datetime.datetime.now()
    html = ('<html><body>'
            'It is now %s, according to admin_custom_view...'
            '</body></html>' % now)
    return HttpResponse(html)


def job_schedule(request):
    jobs = Job.objects.all()
    return render_to_response('protrac/admin_schedule.html', locals(),
            context_instance=RequestContext(request))
