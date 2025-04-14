from celery import shared_task

def get_lower_ranked_officer(current_employee):
    current_rank = current_employee.rank
    department = current_employee.department

    # Search for someone with a higher numerical rank (i.e., lower in hierarchy)
    return Employee.objects.filter(
        department=department,
        rank__gt=current_rank
    ).order_by('rank').first()  # Gets the lowest possible next officer

@shared_task
def send_reminder_email(visit_id):
    from .models import Visit  # Adjust import to your app structure
    visit = Visit.objects.get(id=visit_id)

    if visit.status != 'Pending':
        return  # Do nothing if already handled

    visit.reminder_count += 1
    visit.save()

    if visit.reminder_count >= 5:
        if visit.purpose == 'Personal':
            visit.status = 'Declined'
            visit.save()
            send_email_to_visitor(visit, message="Your visit was declined due to no response.")
        elif visit.purpose == 'Official':
            next_officer = get_lower_ranked_officer(visit.employee)
            if next_officer:
                visit.forwarded_to = next_officer
                visit.employee = next_officer
                visit.save()
                send_email_to_employee(next_officer, visit)
            else:
                visit.status = 'Declined'
                visit.save()
                send_email_to_visitor(visit, message="Your visit could not be attended to.")
        return

    # Otherwise, send regular reminder
    send_email_to_employee(visit.employee, visit)
