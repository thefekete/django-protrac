from django.contrib import messages
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

    See https://docs.djangoproject.com/en/dev/ref/contrib/messages/ for how to
    use messages in templates.

    """
    departments = DEPARTMENT_CHOICES
    production_lines = ProductionLine.objects.order_by('name')

    if request.method == 'POST':
        formset = PriorityFormSet(request.POST)
        if formset.is_valid():
            # need atomic commit of all jobs before prioritization
            for form in formset:
                job = form.save(commit=False) # just save instance to variable
                job.save(no_prioritize=True)
            # prioritize now, after saving jobs
            for line in production_lines:
                line.prioritize()
            messages.success(request, 'Priority successfully updated')
        else:
            error_message = formset.error_class(formset.errors).as_ul()
            messages.error(request, error_message)
            pass

    if department is not None:
        production_lines = production_lines.filter(department=department)
        # get the department key and display value
        department = [ dept for dept in DEPARTMENT_CHOICES
                       if dept[0] == department ][0]

    for line in production_lines:
        line.formset = PriorityFormSet(queryset=line.scheduled_jobs())

    return render_to_response(
            'admin/protrac/schedule.html',
            {
                'departments': departments,
                'production_lines': production_lines,
                'department': department,
            },
            context_instance=RequestContext(request))
