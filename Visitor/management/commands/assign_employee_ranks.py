from django.core.management.base import BaseCommand
from Visitor.models import Employee

class Command(BaseCommand):
    help = 'Assign ranks to employees in each department manually'

    def handle(self, *args, **options):
        department_groups = {}

        # Group employees by department
        for emp in Employee.objects.all():
            dept = emp.department.name
            if dept not in department_groups:
                department_groups[dept] = []
            department_groups[dept].append(emp)

        for dept, employees in department_groups.items():
            # Sort alphabetically for demo; you can change this to your logic
            employees.sort(key=lambda x: x.name)

            for i, emp in enumerate(employees, start=1):
                emp.rank = i  # 1 is top rank
                emp.save()
                self.stdout.write(self.style.SUCCESS(f"{emp.name} in {dept} assigned rank {i}"))

        self.stdout.write(self.style.SUCCESS("All ranks assigned successfully."))
