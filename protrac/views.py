from django.shortcuts import render_to_response
from django.template import RequestContext

from protrac.app_settings import DEPARTMENT_CHOICES
from protrac.models import ProductionLine
from protrac.forms import PriorityFormSet


def schedule(request, department=None):
    """
    Shows scheduled jobs by production_line. Filters by department if given.

    A formset for the prioritization of scheduled jobs is assigned to each
    production line as ProductionLine.formset. This can then be used to
    generate the tables in the template by iterating over ''production_lines'',
    ''formset'', and finaly ''form''. The Job object is accessable via
    ''form.instance''. The template is also passed DEPARTMENT_CHOICES for menu
    generation and the department (if given) for the title.

    """
    departments = DEPARTMENT_CHOICES
    production_lines = ProductionLine.objects.order_by('name')

    if request.method == 'POST':
        # process form submission
        pass

    if department is not None:
        production_lines = production_lines.filter(department=department)
        # get the department key and display value
        department = [ dept for dept in DEPARTMENT_CHOICES
                       if dept[0] == department ][0]
        del(dept) # clean up locals()

    for line in production_lines:
        line.formset = PriorityFormSet(queryset=line.scheduled_jobs())
    del(line) # clean up locals()

    return render_to_response('admin/protrac/schedule.html', locals(),
            context_instance=RequestContext(request))
