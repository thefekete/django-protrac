def admin_custom_view(request):
    import datetime
    from django.http import HttpResponse
    now = datetime.datetime.now()
    html = "<html><body>It is now %s, according to admin_custom_view...</body></html>" % now
    return HttpResponse(html)
