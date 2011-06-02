from django.core.urlresolvers import reverse

def get_change_url(obj):
    admin_view = 'admin:%s_%s_change' % (
            obj._meta.app_label, obj._meta.module_name)
    return reverse(admin_view, args=(obj.id,))
