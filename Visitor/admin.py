from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html
from django.shortcuts import redirect
from .models import Employee, Visitor, VisitLog, Department, PredefinedResponse
from django.contrib.auth.models import Group
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth.admin import GroupAdmin
from django.db.models import Count
from adminsortable2.admin import SortableAdminMixin

class EmployeeAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'rank')
    list_filter = ('department',)
    search_fields = ('name', 'email')
    ordering = ('department', 'rank')

admin.site.register(Department)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Visitor)
admin.site.register(VisitLog)
admin.site.register(PredefinedResponse)
try:
    admin.site.register(Group, GroupAdmin)  # Register Group model with custom GroupAdmin
except AlreadyRegistered:
    pass




admin.site.site_header = "IRA Visitor Administration"
admin.site.site_title = "IRA Admin Portal"
admin.site.index_title = "Welcome to IRA Admin Portal"

# ✅ Add this to urls.py
# path('admin/', custom_admin_site.urls),
