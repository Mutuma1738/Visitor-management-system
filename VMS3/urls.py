from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView # ✅ Import custom login view
from django.contrib.auth.views import LogoutView # ✅ Import custom logout view

from Visitor import views
from Visitor.views import (
    register_visitor, check_visitor, log_visit, update_status, get_department_reasons, forward_visit, export_visits_csv,  export_visits_pdf, add_employee, logout_view
)
#from Visitor.admin import custom_admin_site  # ✅ Import custom admin site

def admin_redirect(request):
     return redirect("admin_dashboard")  # ✅ Redirect to dashboard

urlpatterns = [
    path("accounts/login/", LoginView.as_view(template_name="login.html"), name="admin_login"),  # ✅ Custom login page
    #path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),  # ✅ Custom logout page
    path('admin/', admin_redirect),
    #path('admin/',admin.site.urls),  # ✅ Redirect to dashboard
    path('admin/dashboard/', views.admin_dashboard, name="admin_dashboard"),  # ✅ Custom dashboard
    path('', views.home, name='home'),  
    path('register/', register_visitor, name='register_visitor'),  
    path('check_visitor/', check_visitor, name='check_visitor'),
    path('log_visit/', log_visit, name='log_visit'),  
    path("update_status/<int:visit_id>/", update_status, name="update_status"),
    path('get_department_reasons/', get_department_reasons, name='get_department_reasons'),
    path('forward_visit/<int:visit_id>/', forward_visit, name='forward_visit'),
    path("export/csv/", export_visits_csv, name="export_visits_csv"),
    #path("export/excel/", export_visits_excel, name="export_visits_excel"),
    path("export/pdf/", export_visits_pdf, name="export_visits_pdf"),
    # # Custom admin login/logout (if needed)
    # path("accounts/login/", auth_views.LoginView.as_view(template_name="admin/login.html"), name="admin_login"),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),    
    path('admin/add_employee/', add_employee, name='add_employee'),  # New route
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
]

