from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from protrac.app_settings import DEPARTMENT_CHOICES
from protrac.models import ProductionLine


def schedule(request, line_id=None):
    """
    Shows all scheduled jobs grouped by production_line and line
    department. This view also provides the ability to change priority of jobs
    and record Runs as well.

    """
    if line_id is None:
        # get first production line by name
        pk = ProductionLine.objects.order_by('name')[0].pk
        return redirect('admin:schedule', line_id=pk)
    else:
        line = ProductionLine.objects.get(pk=line_id)
        del(line_id)  # clean up locals before we pass it to template
        return render_to_response('admin/protrac/schedule.html', locals(),
                context_instance=RequestContext(request))
