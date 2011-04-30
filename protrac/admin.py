from django.contrib import admin
from models import *


# Model Admin Inlines

class RunInline(admin.TabularInline):
    model = Run


# Model Admins

admin.site.register(Customer)
admin.site.register(Department)
admin.site.register(Station)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['part_number', 'description', 'cycle_time', 'material_wt',
        'department']
    list_filter = ['department']
    list_display_links = ['part_number']
    readonly_fields = ['ctime', 'mtime']
admin.site.register(Product, ProductAdmin)


JOB_LIST_DISPLAY = ['position', 'id', 'product_department', 'station',
    'product', 'product_description', 'customer', 'refs', 'due_date',
    'balance', 'weight_balance', 'duration_balance', 'closed', 'void']


class JobAdmin(admin.ModelAdmin):
    list_display = JOB_LIST_DISPLAY
    list_display_links = ['id']
    list_editable = ['position', 'station']
    list_filter = ['closed', 'product__department', 'station', 'customer', 'product']
    search_fields = ['refs', 'product__part_number', 'customer__name']
    readonly_fields = ['ctime', 'mtime']

    inlines = [RunInline]

    def product_department(self, obj):
        return obj.product.department

    def product_description(self, obj):
        desc = obj.product.description
        if len(desc) > 32:
            return desc[:32] + '...'
        else:
            return desc

    def weight_balance(self, obj):
        return '%.1f lbs.' % obj.weight_balance()

    def balance(self, obj):
        return u'%i / %i' % (obj.qty_balance(), obj.qty)
admin.site.register(Job, JobAdmin)


class JobScheduleAdmin(JobAdmin):
    ld = list(JOB_LIST_DISPLAY)
    ld.remove('void')
    list_display = ld
    def queryset(self, request):
        return self.model.objects.filter(station__isnull=False, closed=False)
admin.site.register(JobSchedule, JobScheduleAdmin)


class JobLogAdmin(JobAdmin):
    ld = list(JOB_LIST_DISPLAY)
    ld.remove('void')
    list_display = ld
    def queryset(self, request):
        return self.model.objects.filter(void=False)
admin.site.register(JobLog, JobLogAdmin)


class RunAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'start', 'end', 'qty', 'weight', 'cycle_time',
        'operator']
    readonly_fields = ['ctime', 'mtime']
admin.site.register(Run, RunAdmin)
