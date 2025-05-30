# from django.db import models
# from django.utils.timezone import now
# from datetime import timedelta
# from django.utils import timezone
# from django.contrib.auth.models import User
# # from adminsortable2.admin import SortableAdminMixin  # For admin
# #create your models here
# # class Department(models.Model):
# #     name = models.CharField(max_length=255, unique=True)
# #     official_reasons = models.JSONField(default=list)  # Store predefined reasons as a list

# #     def __str__(self):
# #         return self.name

# # class Employee(models.Model):
# #     ROLE_CHOICES = [
# #         ('Director', 'Director'),
# #         ('Manager', 'Manager'),
# #         ('Officer', 'Officer'),
# #         ('Staff', 'Staff'),
# #         ('Intern', 'Intern'),
# #     ]
# #     name = models.CharField(max_length=255)
# #     email = models.EmailField(unique=True)
# #     department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
# #     rank = models.PositiveIntegerField(default=0)  #Lower rank means higher authority
# #     order = models.PositiveIntegerField(default=0)  # Add an order field for sorting
    
# #     class Meta:
# #         ordering = ['order']  # Make sure the ordering is based on 'order' field

# #     def __str__(self):
# #         return self.name

# class Visitor(models.Model):
#     Id_number = models.CharField(max_length=20, unique=True)
#     name = models.CharField(max_length=255)
#     mobile = models.CharField(max_length=15)
#     email = models.EmailField()
    
#     def __str__(self):
#         return f"{self.name} ({self.Id_number})"

# # class Directorate(models.Model):
# #     name = models.CharField(max_length=100)
# #     director_name = models.CharField(max_length=100)

# #     def __str__(self):
# #         return f"{self.name} (Director: {self.director_name})"

# # class Department(models.Model):
# #     name = models.CharField(max_length=100)
# #     directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE, null=True, blank=True)
# #     senior_manager_name = models.CharField(max_length=100)

# #     def __str__(self):
# #         return f"{self.name} ({self.directorate.name if self.directorate else 'No Directorate'})"

# class Directorate(models.Model):
#     name = models.CharField(max_length=100)
#     director = models.OneToOneField('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='director_of')

#     def __str__(self):
#         return self.name
    
# class Department(models.Model):
#     name = models.CharField(max_length=100)
#     directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE)
#     senior_manager = models.OneToOneField('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='senior_manager_of')

#     def __str__(self):
#         return self.name

# # class Employee(models.Model):
# #     DESIGNATION_CHOICES = [
# #         ('Director', 'Director'),
# #         ('Senior Manager', 'Senior Manager'),
# #         ('Junior Manager', 'Junior Manager'),
# #         ('Officer', 'Officer'),
# #         ('Staff', 'Staff'),
# #         ('Intern', 'Intern'),
# #         ('Attachee', 'Attachee'),
# #     ]

# #     first_name = models.CharField(max_length=100)
# #     last_name = models.CharField(max_length=100)
# #     email = models.EmailField(unique=True)
# #     department = models.ForeignKey(Department, on_delete=models.CASCADE)
# #     designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)

# #     def __str__(self):
# #         return f"{self.first_name} {self.last_name}"

# DESIGNATION_CHOICES = [
#     ('CEO', 'CEO'),
#     ('Director', 'Director'),
#     ('Senior Manager', 'Senior Manager'),
#     ('Junior Manager', 'Junior Manager'),
#     ('Employee', 'Employee'),
#     ('Attachee', 'Attachee'),
# ]

# class Employee(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)

#     # ✅ Add these two lines:
#     directorate = models.ForeignKey('Directorate', on_delete=models.SET_NULL, null=True, blank=True)
#     department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"


# class VisitLog(models.Model):
#     PURPOSE_CHOICES = [
#         ('Personal', 'Personal'),
#         ('Official', 'Official'),
#     ]
#     STATUS_CHOICES = [
#         ('Pending', 'Pending'),
#         ('Approved', 'Approved'),
#         ('Declined', 'Declined'),
#         ('Forwarded', 'Forwarded'),
#     ]
#     visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_visits')
#     forwarded_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='forwarded_visits_received')
#     purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
#     description = models.TextField(blank=True, null=True)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')  # Use STATUS_CHOICES here
#     comments = models.TextField(blank=True, null=True)  # ✅ New field for comments    
#     arrival_time = models.DateTimeField(null=True, blank=True)
#     delayed_arrival_time = models.DateTimeField(null=True, blank=True)
#     expiry_duration = models.DurationField(default=timedelta(hours=2))  # e.g., 2 hours by default
#     expiry_time = models.DateTimeField(blank=True, null=True)
#     approved_at = models.DateTimeField(blank=True, null=True)
#     wait_duration = models.DurationField(blank=True, null=True)
#     wait_until = models.DateTimeField(blank=True, null=True)
#     reminder_count = models.PositiveIntegerField(default=0)
#     forwarded_from = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='forwarded_visits_sent')

#     def approve(self, wait_duration=None):
#         self.status = 'Approved'
#         self.approved_at = timezone.now()

#         if wait_duration:
#             self.wait_duration = wait_duration
#             self.wait_until = self.approved_at + wait_duration
#         else:
#             self.wait_duration = None
#             self.wait_until = None

#         self.save()

#     def save(self, *args, **kwargs):
#         if not self.expiry_time:
#             self.expiry_time = self.arrival_time + self.expiry_duration
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.visitor.name} - {self.arrival_time}"

# class PredefinedResponse(models.Model):
#     STATUS_CHOICES = [
#         ("Approved", "Approved"),
#         ("Declined", "Declined"),
#         ("Forwarded", "Forwarded"),
#     ]
    
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)
#     response_text = models.TextField()

#     def __str__(self):
#         return f"{self.status} - {self.response_text[:30]}"  # Display first 30 chars in admin
from django.db import models
from django.utils import timezone
from datetime import timedelta

# ========== Core Models ==========

class Visitor(models.Model):
    Id_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} ({self.Id_number})"


DESIGNATION_CHOICES = [
    ('CEO', 'CEO'),
    ('Director', 'Director'),
    ('Senior Manager', 'Senior Manager'),
    ('Junior Manager', 'Junior Manager'),
    ('Employee', 'Employee'),
    ('Attachee', 'Attachee'),
]

class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)
    directorate = models.ForeignKey('Directorate', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Directorate(models.Model):
    name = models.CharField(max_length=100)
    director = models.OneToOneField('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='director_of')

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE)
    senior_manager = models.OneToOneField('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='senior_manager_of')
    official_reasons = models.JSONField(default=list, blank=True, null=True)  # ✅ Added to support get_department_reasons view

    def __str__(self):
        return self.name


# ========== Visit Log and Responses ==========

class VisitLog(models.Model):
    PURPOSE_CHOICES = [
        ('Personal', 'Personal'),
        ('Official', 'Official'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
        ('Forwarded', 'Forwarded'),
    ]

    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_visits')
    forwarded_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='forwarded_visits_received')
    forwarded_from = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='forwarded_visits_sent')
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    comments = models.TextField(blank=True, null=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    delayed_arrival_time = models.DateTimeField(null=True, blank=True)
    expiry_duration = models.DurationField(default=timedelta(hours=2))
    expiry_time = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    wait_duration = models.DurationField(blank=True, null=True)
    wait_until = models.DateTimeField(blank=True, null=True)
    reminder_count = models.PositiveIntegerField(default=0)

    def approve(self, wait_duration=None):
        self.status = 'Approved'
        self.approved_at = timezone.now()

        if wait_duration:
            self.wait_duration = wait_duration
            self.wait_until = self.approved_at + wait_duration
        else:
            self.wait_duration = None
            self.wait_until = None

        self.save()

    def save(self, *args, **kwargs):
        if self.arrival_time and not self.expiry_time:
            self.expiry_time = self.arrival_time + self.expiry_duration
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.visitor.name} - {self.arrival_time}"


class PredefinedResponse(models.Model):
    STATUS_CHOICES = [
        ("Approved", "Approved"),
        ("Declined", "Declined"),
        ("Forwarded", "Forwarded"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response_text = models.TextField()

    def __str__(self):
        return f"{self.status} - {self.response_text[:30]}"

