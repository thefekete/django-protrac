from django.shortcuts import render_to_response
from django.template import RequestContext

from app_settings import LINE_CATEGORY_CHOICES
from models import ProductionLine


def schedule(request):
    """
    Shows all scheduled jobs grouped by production_line and line
    category. This view also provides the ability to change priority of jobs
    and record Runs as well.

    """
    # FIXME: Need to make reality match docstring
    objects = [ (cat, ProductionLine.objects.filter(category=abbr))
            for (abbr, cat) in LINE_CATEGORY_CHOICES ]
    return render_to_response('admin/protrac/schedule.html', locals(),
            context_instance=RequestContext(request))
