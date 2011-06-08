from django.contrib import admin
from django.conf.urls.defaults import patterns
from django.template.defaultfilters import force_escape
from models import *
from utils import get_change_url


# Model Admin Inlines

class RunInline(admin.TabularInline):
    model = Run


# Model Admins

admin.site.register(Customer)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['part_number', 'description', 'cycle_time', 'material_wt',
        'department']
    list_filter = ['department']
    list_display_links = ['part_number']
    readonly_fields = ['ctime', 'mtime']
    a_fieldsets = (
        ('Dates', {
            'fields': ('ctime', 'mtime')
        }),
    )
admin.site.register(Product, ProductAdmin)


JOB_LIST_DISPLAY = ['__unicode__', 'priority', 'product_department',
    'production_line', 'product_admin_link', 'product_description', 'customer',
    'refs', 'due_date', 'remaining', 'weight_remaining', 'duration_remaining',
    'suspended', 'void']


class JobAdmin(admin.ModelAdmin):
    list_display = JOB_LIST_DISPLAY
    list_display_links = ['__unicode__']
    list_editable = ['priority', 'production_line']
    list_filter = ['product__department', 'production_line', 'customer', 'product']
    search_fields = ['refs', 'product__part_number', 'customer__name']
    readonly_fields = ['ctime', 'mtime']

    inlines = [RunInline]

    def product_department(self, obj):
        return obj.product.get_department_display()

    def product_description(self, obj):
        desc = obj.product.description
        if len(desc) > 32:
            return desc[:32] + '...'
        else:
            return desc

    def product_admin_link(self, obj):
        p = obj.product
        return u'<a href="%s" title="%s">%s</a>' % (
            get_change_url(p), force_escape(p.description), force_escape(p))
    product_admin_link.allow_tags = True
    product_admin_link.short_description = 'Product'

    def weight_remaining(self, obj):
        try:
            return '%.1f lbs.' % obj.weight_remaining()
        except TypeError:
            return None

    def remaining(self, obj):
        style = 'font-weight: bold;'
        if obj.qty_done() >= obj.qty:
            style += ' color: green;'
        elif obj.qty_done() > 0:
            style += ' color: orange;'
        else:
            style += ' color: red;'
        return u'<span style="%s">%i / %i</span>' % (
            style, obj.qty_remaining(), obj.qty)
    remaining.allow_tags = True
admin.site.register(Job, JobAdmin)


class ScheduleAdmin(JobAdmin):
    ld = list(JOB_LIST_DISPLAY)
    ld.remove('void')
    list_display = ld

    def get_urls(self):
        urls = super(ScheduleAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^my_view/$', self.admin_site.admin_view(self.my_view))
        )
        return my_urls + urls

    def my_view(self, request):
        import datetime
        from django.http import HttpResponse
        now = datetime.datetime.now()
        html = "<html><body>It is now %s.</body></html>" % now
        return HttpResponse(html)
admin.site.register(Schedule, ScheduleAdmin)


class RunAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'job_admin_link', 'start', 'end', 'qty', 'weight', 'cycle_time',
        'operator']
    readonly_fields = ['ctime', 'mtime']

    def job_admin_link(self, obj):
        j = obj.job
        return u'<a href="%s">%s</a>' % (
            get_change_url(j), j)
    job_admin_link.allow_tags = True
    job_admin_link.short_description = 'Job'
admin.site.register(Run, RunAdmin)
