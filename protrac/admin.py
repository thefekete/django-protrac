from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.template.defaultfilters import force_escape

from models import *
from utils import get_change_url


#######################
# Model Admin Inlines #
#######################

class RunInline(admin.TabularInline):
    model = Run


################
# Model Admins #
################

class CustomerAdmin(admin.ModelAdmin):
    search_fields = ('name',)
admin.site.register(Customer, CustomerAdmin)


class ProductionLineAdmin(admin.ModelAdmin):
    display_links = ['name',]
    list_filter = ['category']
admin.site.register(ProductionLine, ProductionLineAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['part_number', 'material', 'cycle_time',
            'avg_cycle_time']
    list_display_links = ['part_number']
    readonly_fields = ['ctime', 'mtime']
    search_fields = ['part_number', 'description']
    fieldsets = (
        (None, {
            'fields': ('part_number', ('cycle_time',
                'material_wt'),)
            }),
        ('Detailed Informaion', {
            'fields': ('description', 'setup')
            }),
        ('Creation/Modification Times', {
            'classes': ('collapse',),
            'fields': ('ctime', 'mtime')
            }),
        )

    def material(self, obj):
        return u'%f lbs' % obj.material_wt
admin.site.register(Product, ProductAdmin)


JOB_LIST_DISPLAY = ['__unicode__', 'priority', 'production_line',
    'product_admin_link', 'customer', 'refs', 'remaining',
    'weight_remaining', 'duration_remaining', 'avg_cycle_time', 'suspended',
    'void']


class JobAdmin(admin.ModelAdmin):
    list_display = JOB_LIST_DISPLAY
    list_display_links = ['__unicode__']
    list_editable = ['priority', 'production_line']
    list_filter = ['production_line', 'customer', 'product']
    search_fields = ['refs', 'product__part_number', 'customer__name']
    readonly_fields = ['ctime', 'mtime']

    fieldsets = (
        (None, {
            'fields': (('production_line', 'priority'), ('suspended',
                'void'))
            }),
        ('Order Info', {
            'fields': (('customer', 'due_date'), 'refs', ('product',
                'qty'))
            }),
        ('Creation/Modification Times', {
            'classes': ('collapse',),
            'fields': ('ctime', 'mtime')
            }),
        )

    inlines = [RunInline]

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
            return '%.1f lbs' % obj.weight_remaining()
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

    def get_urls(self):
        from views import job_schedule
        urls = super(JobAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^job_schedule', self.admin_site.admin_view(job_schedule),
                name='job_schedule'),
        )
        return my_urls + urls

admin.site.register(Job, JobAdmin)


class RunAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'job_admin_link', 'start', 'end', 'qty',
           'weight', 'cycle_time', 'operator']
    readonly_fields = ['ctime', 'mtime']
    search_fields = ['job__product__part_number', 'job__customer__name',
           'job__refs', 'operator',]
    fieldsets = (
        (None, {
            'fields': (('job', 'qty'), 'operator', 'start', 'end')
            }),
        ('Creation/Modification Times', {
            'classes': ('collapse',),
            'fields': ('ctime', 'mtime')
            }),
        )

    def job_admin_link(self, obj):
        j = obj.job
        return u'<a href="%s">%s</a>' % (
            get_change_url(j), j)
    job_admin_link.allow_tags = True
    job_admin_link.short_description = 'Job'
admin.site.register(Run, RunAdmin)


class ScheduleAdmin(JobAdmin):
    ld = list(JOB_LIST_DISPLAY)
    ld.remove('void')
    list_display = ld

    # Disable Job addition from proxy model admin (still allow change)
    def has_add_permission(self, request):
        return False

    # Disable Job deletion from proxy model admin
    def has_delete_permission(self, request):
        return False

    # Overrides/extends admin view to include more context
    def changelist_view(self, request, extra_context=None):
        my_context = { 'pen15': 'How\'s about that?!' }
        return super(ScheduleAdmin, self).changelist_view(request,
                extra_context=my_context)

    # Adds urls to admin area
    # self.admin_site.admin_view() adds admin security and stuff to view
    def get_urls(self):
        from views import admin_custom_view
        urls = super(ScheduleAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^my_view', self.admin_site.admin_view(self.my_view)),
            url(r'^admin_custom_view',
                self.admin_site.admin_view(admin_custom_view),
                name='admin_custom_view')
        )
        return my_urls + urls

    def my_view(self, request):
        """
        Example view definition in admin class definition
        """
        import datetime
        from django.http import HttpResponse
        now = datetime.datetime.now()
        html = "<html><body>It is now %s.</body></html>" % now
        return HttpResponse(html)
admin.site.register(Schedule, ScheduleAdmin)
