from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.db.models import Count
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.contrib.auth.decorators import login_required
from datetime import timedelta, datetime, date
from django.db.models.functions import TruncDate
from .forms import EmployeeForm  # Create this form
from django.conf import settings
# Import necessary visualization libraries
from django.core.serializers.json import DjangoJSONEncoder
import json
import os
import smtplib
#import settings
#import pandas as pd
#import for downloading data
import csv
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.utils.timezone import is_aware
from django.utils.dateparse import parse_date
from django.utils import timezone
#For Reminders
from celery import shared_task
from django.utils import timezone

#Admin Authentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def home(request):
    """Render the visitor registration form as the home page."""
    employees = Employee.objects.all()
    return render(request, "register_visitor.html", {"employees": employees})

def check_visitor(request):
    """Check if a visitor exists and return their details."""
    Id_number = request.GET.get('Id_number', None)
    visitor = Visitor.objects.filter(Id_number=Id_number).first()
    
    if visitor:
        return JsonResponse({
            'name': visitor.name,
            'mobile': visitor.mobile,
            'email': visitor.email,
            'exists': True
        })
    return JsonResponse({'exists': False, 'message': "ID not found. Please fill in your details."})

def register_visitor(request):
    """Register a new visitor."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            id_number, name, mobile = data.get('Id_number'), data.get('name'), data.get('mobile')

            if not all([id_number, name, mobile]):
                return JsonResponse({'error': 'All fields are required'}, status=400)

            if Visitor.objects.filter(Id_number=id_number).exists():
                return JsonResponse({'error': 'Visitor already registered'}, status=400)

            visitor = Visitor.objects.create(Id_number=id_number, name=name, mobile=mobile)
            return JsonResponse({'message': 'Visitor registered successfully', 'visitor_id': visitor.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def send_smtp_email(to_email, subject, message):
    """Send an email using Django's built-in email backend."""
    try:
        send_mail(
            subject,
            message,  # Plain text message (HTML is handled separately)
            settings.EMAIL_HOST_USER,
            [to_email] if isinstance(to_email, str) else to_email,  # Supports multiple recipients
            fail_silently=False,
            html_message=message,  # HTML content for rich email formatting
        )
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

def log_visit(request):
    """Log a visit and notify the chosen employee via email."""
    try:
        if request.method == "POST":
            Id_number = request.POST.get("Id_number")
            visitor = Visitor.objects.filter(Id_number=Id_number).first()
            if not visitor:
                return redirect('home')

            employee_id = request.POST.get("employee")
            purpose = request.POST.get("purpose")
            official_reason = request.POST.get("official_reason", "").strip()
            other_reason = request.POST.get("other_reason", "").strip()
            description = other_reason if other_reason else official_reason

            try:
                employee = Employee.objects.get(id=employee_id)
            except Employee.DoesNotExist:
                return JsonResponse({"error": "Selected employee not found."}, status=400)

            # Create a new visit log entry
            visit_log = VisitLog.objects.create(
                visitor=visitor,
                employee=employee,
                purpose=purpose,
                description=description,
                status="Pending",
                arrival_time=timezone.now()  # Sets the arrival time to the current time

            )

            # Send initial email to the employee with options
            message = f"""
            Dear {employee.first_name}{employee.last_name},<br><br>
            You have a new visit request from {visitor.name} ({visitor.Id_number}).<br>
            <strong>Purpose:</strong> {purpose}<br>
            <strong>Description:</strong> {visit_log.description}<br><br>
            
            Kindly advise on this request <br>
            <a href="http://10.25.5.47:8000/update_status/{visit_log.id}/?status=Approved">✅ Approve</a> |
            <a href="http://10.25.5.47:8000/update_status/{visit_log.id}/?status=Declined">❌ Decline</a> |
            <a href="http://10.25.5.47:8000/forward_visit/{visit_log.id}/">🔄 Forward</a><br><br>
            
            Best regards,<br>
            Insurance Regulatory Authority
            """
            send_smtp_email(employee.email, "New Visit Request", message)

            # Schedule the reminder task to run 10 minutes later
            # After logging visit
            # send_reminder_email.apply_async(
            #     args=[visit_log.id, 1, 5],  # start with iteration 1, max 5 reminders
            #     countdown=60
            # )


        # return redirect('home')
        return JsonResponse({'success': True, 'message': 'Visit logged successfully'})
    except Exception as e:
            print("❌ Error in log_visit:", e)
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': 'Internal server error'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def forward_visit(request, visit_id):
    """Allows an employee to forward a visit to another employee with comments."""
    visit = get_object_or_404(VisitLog, id=visit_id)
    employees = Employee.objects.exclude(id=visit.employee.id)  # Exclude the current employee

    if request.method == "POST":
        new_employee_id = request.POST.get("new_employee_id")
        comment = request.POST.get("comment", "").strip()

        if not new_employee_id:
            return JsonResponse({"error": "No new employee selected."}, status=400)

        if not comment:
            return JsonResponse({"error": "A comment is required"}, status=400)

        try:
            new_employee = Employee.objects.get(id=new_employee_id)
        except Employee.DoesNotExist:
            return JsonResponse({"error": "Selected employee does not exist."}, status=400)

        # Update visit log
        visit.forwarded_to = new_employee
        visit.status = "Forwarded"
        visit.comments = comment  # Store comment for reference
        visit.save()

        # Notify the next employee (Chocolate) about the forwarded visitor
        message = f"""
        The following visitor has been forwarded to you by {visit.employee.name}.<br><br>
        <strong>Visitor:</strong> {visit.visitor.name} ({visit.visitor.Id_number})<br>
        <strong>Previous Employee:</strong> {visit.employee.name}<br>
        <strong>Comment:</strong> {comment}<br><br>

        Please take action:<br>
        <a href="http://127.0.0.1:8000/update_status/{visit.id}/">✅ Approve</a> |
        <a href="http://127.0.0.1:8000/update_status/{visit.id}/">❌ Decline</a> |
        <a href="http://127.0.0.1:8000/forward_visit/{visit.id}/">🔁 Forward</a><br><br>

        Regards,<br>
        Visitor Management System
        """
        send_smtp_email(new_employee.email, "Visitor Forwarded to You", message)

        return JsonResponse({"message": f"Visitor has been forwarded to {new_employee.name}."})

    return render(request, "forward_visit.html", {"visit": visit, "employees": employees})

def update_status(request, visit_id):
    """Handles approval, decline, or forwarding of visit requests with comments and optional wait duration."""
    visit = get_object_or_404(VisitLog, id=visit_id)

    if request.method == "POST":
        status = request.POST.get("status")
        comment = request.POST.get("comment", "").strip()
        wait_minutes = request.POST.get("wait_minutes")

        if status not in ["Approved", "Declined", "Forwarded"]:
            return JsonResponse({"error": "Invalid status"}, status=400)

        if not comment:
            return JsonResponse({"error": "A comment is required"}, status=400)

        # Set basic fields
        visit.status = status
        visit.comments = comment

        # ✅ Handle wait time if approved
        if status == "Approved":
            visit.approved_at = timezone.now()

            if wait_minutes and wait_minutes.isdigit() and int(wait_minutes) > 0:
                wait_duration = timedelta(minutes=int(wait_minutes))
                visit.wait_duration = wait_duration
                visit.wait_until = visit.approved_at + wait_duration
            else:
                visit.wait_duration = None
                visit.wait_until = None

        visit.save()

        # ✅ Send notification to visitor
        wait_note = ""
        if status == "Approved" and visit.wait_until:
            wait_time = visit.wait_until.strftime('%H:%M %p')
            wait_note = f"<br><strong>Wait Until:</strong> {wait_time}. Please wait at the reception until then."

        # Send visitor notification email
        visitor_subject = f"Visit Request {status} - {visit.visitor.name}"
        visitor_message = f"""
        Hello {visit.visitor.name},<br><br>
        Your visit request has been {status}.<br><br>
        <strong>Employee:</strong> {visit.employee.name}<br>
        <strong>Status:</strong> {status}<br>
        <strong>Comment:</strong> {comment}<br>{wait_note}<br><br>

        Thank you,<br>
        Visitor Management System
        """
        send_smtp_email(SMTP_USERNAME, visitor_subject, visitor_message)

        # Send email to system or employee as needed
        subject = f"Visit Request {status} - {visit.visitor.name}"
        message = f"""
        A decision has been made regarding the visit request.<br><br>
        <strong>Visitor:</strong> {visit.visitor.name} ({visit.visitor.Id_number})<br>
        <strong>Employee:</strong> {visit.employee.name}<br>
        <strong>Status:</strong> {status}<br>
        <strong>Comment:</strong> {comment}{wait_note}<br><br>

        Regards,<br>
        Visitor Management System
        """
        send_smtp_email(SMTP_USERNAME, subject, message)

        return JsonResponse({"message": f"Visit has been {status}. Notification sent to the system and visitor."})

    # Get predefined responses
    predefined_responses = {
        "Approved": list(PredefinedResponse.objects.filter(status="Approved").values_list("response_text", flat=True)),
        "Declined": list(PredefinedResponse.objects.filter(status="Declined").values_list("response_text", flat=True)),
        "Forwarded": list(PredefinedResponse.objects.filter(status="Forwarded").values_list("response_text", flat=True)),
    }

    return render(request, "update_status.html", {
        "visit": visit,
        "predefined_responses": predefined_responses
    })

def get_department_reasons(request):
    employee_id = request.GET.get("employee_id")

    if not employee_id:
        return JsonResponse({"error": "No employee ID provided"}, status=400)

    try:
        employee = get_object_or_404(Employee, id=employee_id)

        if employee.department:
            # Fetch reasons from the department
            reasons = employee.department.official_reasons
        elif employee.directorate and not employee.department:
            # Fetch reasons directly from the directorate
            reasons = employee.directorate.official_reasons
        else:
            return JsonResponse({"error": "No department or directorate found for employee"}, status=404)

        return JsonResponse({"reasons": reasons})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)@login_required
        
def admin_dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponse("You are not logged in. Please log in to access this page.", status=403)

    # Get date filters from GET parameters
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Convert to actual dates
    start_date = parse_date(start_date_str) if start_date_str else None
    end_date = parse_date(end_date_str) if end_date_str else None

    # Filter visits based on dates
    visits = VisitLog.objects.all()
    if start_date and end_date:
        visits = visits.filter(arrival_time__date__range=(start_date, end_date))
    elif start_date:
        visits = visits.filter(arrival_time__date__gte=start_date)
    elif end_date:
        visits = visits.filter(arrival_time__date__lte=end_date)

    # Proceed with all analytics using the filtered `visits` queryset
    total_visits = visits.count()
    total_visitors = visits.values('visitor').distinct().count()
    total_employees = visits.values('employee').distinct().count()
    pending_visits = visits.filter(status='Pending').count()

    most_visited_employee = Employee.objects.annotate(
        visit_count=Count('assigned_visits')
    ).order_by('-visit_count').first()

    most_forwarded_to_employee = Employee.objects.annotate(
        forwarded_to_count=Count('forwarded_visits_received')
    ).order_by('-forwarded_to_count').first()

    most_forwarding_employee = Employee.objects.annotate(
        forwarded_from_count=Count('forwarded_visits_sent')
    ).order_by('-forwarded_from_count').first()


    most_visited_department = Department.objects.annotate(
        visit_count=Count('employee__assigned_visits') + Count('employee__forwarded_visits_received')
    ).order_by('-visit_count').first()

    visit_purpose_data = list(visits.values('purpose').annotate(count=Count('id')))
    visit_purpose_labels = [item['purpose'] for item in visit_purpose_data]
    visit_purpose_values = [item['count'] for item in visit_purpose_data]

    department_visits = Department.objects.annotate(
        visit_count=Count('employee__assigned_visits') + Count('employee__forwarded_visits_received')
    )
    department_labels = [d.name for d in department_visits]
    department_values = [d.visit_count for d in department_visits]

    approval_rejection_data = [
        visits.filter(status='Approved').count(),
        visits.filter(status='Declined').count()
    ]

    # Visitor trend analysis based on the same date range
    visitor_trend_queryset = visits.annotate(date=TruncDate('arrival_time')) \
        .values('date').annotate(count=Count('id')).order_by('date')

    visitor_trend_labels = [entry['date'].strftime('%Y-%m-%d') for entry in visitor_trend_queryset if entry['date']]
    visitor_trend_data = [entry['count'] for entry in visitor_trend_queryset]

    context = {
        'total_visits': total_visits,
        'total_visitors': total_visitors,
        'total_employees': total_employees,
        'pending_visits': pending_visits,
        'most_visited_employee': f"{most_visited_employee.first_name} {most_visited_employee.last_name}" if most_visited_employee else "N/A",
        'most_visited_department': most_visited_department.name if most_visited_department else "N/A",
        'visit_purpose_labels': json.dumps(visit_purpose_labels),
        'visit_purpose_data': json.dumps(visit_purpose_values),
        'department_labels': json.dumps(department_labels),
        'department_data': json.dumps(department_values),
        'approval_rejection_data': json.dumps(approval_rejection_data),
        'visitor_trend_labels': json.dumps(visitor_trend_labels),
        'visitor_trend_data': json.dumps(visitor_trend_data),
        'request': request  # so you can use `request.GET` in the template
    }

    return render(request, 'admin_dashboard.html', context)

def export_visits_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    visits = VisitLog.objects.all()

    if start_date and end_date:
        # Convert to date format and filter
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        visits = visits.filter(arrival_time__date__range=(start, end))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="visits.csv"'

    writer = csv.writer(response)
    writer.writerow(['Visitor Name', 'Employee', 'Visit Time', 'Status'])

    for visit in visits:
        writer.writerow([visit.visitor.name, visit.employee.name, visit.arrival_time, visit.status])

    return response

def export_visits_pdf(request):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    visits = VisitLog.objects.all()

    if start_date and end_date:
        # Convert to date format and filter
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        visits = visits.filter(arrival_time__date__range=(start, end))

    """Export visit logs as a PDF file"""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="visit_logs.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, "Visit Logs Report")

    visits = VisitLog.objects.all()
    y_position = 780
    for visit in visits:
        p.drawString(100, y_position, f"{visit.visitor.name} | {visit.employee.name} | {visit.purpose} | {visit.status} | {visit.arrival_time}")
        y_position -= 20

    p.showPage()
    p.save()
    return response

@login_required(login_url='login')
def add_employee(request):
    success_message = request.session.pop('employee_success', None)  # Always check at top

    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            request.session['employee_success'] = 'Employee added successfully!'
            
            # Automatically assign roles based on designation
            if employee.designation == 'Director' and employee.directorate:
                employee.directorate.director = employee
                employee.directorate.save()
            elif employee.designation == 'Senior Manager' and employee.department:
                employee.department.senior_manager = employee
                employee.department.save()

            return redirect('add_employee')  # redirect to prevent form re-submission
    else:
        form = EmployeeForm()

    return render(request, 'admin_add_employee.html', {
        'form': form,
        'success_message': success_message
    })

def departments_by_directorate(request, directorate_id):
    departments = Department.objects.filter(directorate_id=directorate_id)
    data = [{'id': d.id, 'name': d.name} for d in departments]
    return JsonResponse(data, safe=False)

@shared_task
def send_reminder_email(visit_log_id, iteration=1, max_reminders=5):
    try:
        visit = VisitLog.objects.get(id=visit_log_id)
        
        from_email = os.getenv("SMTP_USERNAME", settings.EMAIL_HOST_USER)  # Default to settings if env var not set
        
        # Only remind if still pending and within limit
        if visit.status == "Pending" and iteration <= max_reminders:
            # Send reminder email
            send_mail(
                subject=f"Reminder #{iteration} - Visitor is still waiting",
                message=f"The visitor {visit.visitor.name} is still waiting for your response.",
                from_email=from_email,  # Use the dynamically fetched email here
                recipient_list=[visit.employee.email],
            )

            # Schedule the next reminder in 10 minutes
            send_reminder_email.apply_async(
                args=[visit_log_id, iteration + 1, max_reminders],
                countdown=60  # 10 minutes
            )

    except VisitLog.DoesNotExist:
        pass  # Optionally log error

@shared_task
def process_reminders():
    visits = VisitLog.objects.filter(status='Pending', reminder_count__gte=5)

    for visit in visits:
        if visit.purpose == 'Personal':
            visit.status = 'Declined'
            visit.comments = 'Automatically declined after 5 reminders.'
            visit.save()
            # Notify visitor via email
            # You can send an email here if desired

        elif visit.purpose == 'Official':
            department = visit.employee.department
            original_rank = visit.employee.rank

            lower_officers = Employee.objects.filter(department=department, rank__gt=original_rank).order_by('rank')

            if lower_officers.exists():
                new_employee = lower_officers.first()
                visit.forwarded_from = visit.employee
                visit.forwarded_to = new_employee
                visit.employee = new_employee
                visit.status = 'Forwarded'
                visit.comments = f"Automatically forwarded after 5 reminders from {visit.forwarded_from.name}."
                visit.save()

                send_employee_notification_email(visit)  # Re-use your current email logic

# Corrected code to trigger the task after getting the VisitLog instance
def some_view(request):
    visitlog_id = 1  # Example of how you might get this dynamically, for example from a GET request
    try:
        visitlog = VisitLog.objects.get(id=visitlog_id)
        # Trigger the reminder task after 10 minutes
        send_reminder_email.apply_async((visitlog.id,), countdown=600)  # 600 seconds = 10 minutes
    except VisitLog.DoesNotExist:
        return HttpResponse("VisitLog not found", status=404)

def send_approval_email(visitor_email, employee_email):
    # Send emails to both employee and visitor
    send_mail(
        'Visit Approved',
        f'Your visit has been approved. Please arrive at {visitor_arrival_time}',
        'noreply@vms.com',
        [visitor_email],
        fail_silently=False,
    )

@login_required
def login_redirect(request):
    return redirect("admin_dashboard")  # Redirect to the admin dashboard after login

def logout_view(request):
    logout(request)
    return redirect('/accounts/login/?logged_out=true')

def employee_list(request):
    employees = Employee.objects.select_related('department').all()
    return render(request, 'employee_list.html', {'employees': employees})

# Edit
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            request.session['employee_success'] = 'Employee added successfully!'
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee_form.html', {'form': form, 'action': 'Edit'})

# Delete
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        request.session['employee_success'] = 'Employee deleted successfully!'

        return redirect('employee_list')
    return render(request, 'employee_confirm_delete.html', {'employee': employee})

