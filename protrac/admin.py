from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.template.defaultfilters import force_escape

from models import Customer, Job, Product, ProductionLine, Run
from utils import get_change_url


class CustomerAdmin(admin.ModelAdmin):
    search_fields = ['name']

admin.site.register(Customer, CustomerAdmin)


class ProductionLineAdmin(admin.ModelAdmin):
    display_links = ['name']
    list_filter = ['department']

admin.site.register(ProductionLine, ProductionLineAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['part_number',
                    'material',
                    'cycle_time',
                    'avg_cycle_time']
    list_display_links = ['part_number']
    readonly_fields = ['ctime', 'mtime']
    search_fields = ['part_number', 'description']
    fieldsets = (
        (None, {
            'fields': ['part_number', ('cycle_time', 'material_wt')]
            }),
        ('Detailed Informaion', {
            'fields': ['description', 'setup']
            }),
        ('Creation/Modification Times', {
            'classes': ['collapse'],
            'fields': ['ctime', 'mtime']
            }),
        )

    def material(self, obj):
        return u'%f lbs' % obj.material_wt

admin.site.register(Product, ProductAdmin)


class RunInline(admin.TabularInline):
    model = Run

class JobAdmin(admin.ModelAdmin):
    list_display = ['__unicode__',
                    'priority',
                    'production_line',
                    'product_admin_link',
                    'customer',
                    'refs',
                    'remaining',
                    'weight_remaining',
                    'duration_remaining',
                    'avg_cycle_time',
                    'suspended',
                    'void']
    list_display_links = ['__unicode__']
    list_editable = ['priority', 'production_line']
    list_filter = ['production_line', 'customer', 'product']
    search_fields = ['refs', 'product__part_number', 'customer__name']
    readonly_fields = ['ctime', 'mtime']

    fieldsets = (
        (None, {
            'fields': [('production_line', 'priority'), ('suspended', 'void')]
            }),
        ('Order Info', {
            'fields': [('customer', 'due_date'), 'refs', ('product', 'qty')]
            }),
        ('Creation/Modification Times', {
            'classes': ['collapse'],
            'fields': ['ctime', 'mtime']
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
        # Ties the schedule view into the admin
        from protrac.views import schedule
        urls = super(JobAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^schedule/$',
                self.admin_site.admin_view(schedule), name='schedule'),
            url(r'^schedule/(?P<department>\w+)/$',
                self.admin_site.admin_view(schedule), name='schedule'),
        )
        return my_urls + urls

admin.site.register(Job, JobAdmin)


class RunAdmin(admin.ModelAdmin):
    list_display = ['__unicode__',
                    'job_admin_link',
                    'start',
                    'end',
                    'qty',
                    'weight',
                    'cycle_time',
                    'operator']
    readonly_fields = ['ctime', 'mtime']
    search_fields = ['job__product__part_number', 'job__customer__name',
            'job__refs', 'operator']
    fieldsets = (
        (None, {
            'fields': [('job', 'qty'), 'operator', 'start', 'end']
            }),
        ('Creation/Modification Times', {
            'classes': ['collapse'],
            'fields': ['ctime', 'mtime']
            })
        )

    def job_admin_link(self, obj):
        j = obj.job
        return u'<a href="%s">%s</a>' % (
            get_change_url(j), j)
    job_admin_link.allow_tags = True
    job_admin_link.short_description = 'Job'

admin.site.register(Run, RunAdmin)
