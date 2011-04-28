from django.contrib import admin
from models import *

admin.site.register(Customer)


class OrderLineInline(admin.TabularInline):
    model = OrderLine


class StationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Station, StationAdmin)


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderLineInline]
    list_display = ['customer', 'so_num', 'po_num', 'recieved_date',
        'due_date', 'order_lines']
    list_filter = ['customer']
    list_display_links = ['so_num']
admin.site.register(Order, OrderAdmin)


class OrderLineAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'qty']
    list_filter = ['product', 'order']
admin.site.register(OrderLine, OrderLineAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['part_number', 'description', 'cycle_time']
admin.site.register(Product, ProductAdmin)


class RunAdmin(admin.ModelAdmin):
    list_filter = ['is_closed', 'station']
    list_display = ['id', 'position', 'qty', 'start', 'end', 'real_qty',
                    'is_closed']
    list_editable = ['position']

    def department(self, obj):
        return obj.order_line.product.get_department_display()
admin.site.register(Run, RunAdmin)
