# from django import forms
# from .models import Employee, Directorate, Department

# class EmployeeForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = ['first_name', 'last_name', 'email', 'department', 'designation']
#         widgets = {
#             'first_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'department': forms.Select(attrs={'class': 'form-control'}),
#             'designation': forms.Select(attrs={'class': 'form-control'}),
#         }

from django import forms
from .models import Employee, Directorate, Department

# class EmployeeForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = ['first_name', 'last_name', 'email', 'designation', 'directorate', 'department']

#     def __init__(self, *args, **kwargs):
#         super(EmployeeForm, self).__init__(*args, **kwargs)
#         self.fields['directorate'].required = False
#         self.fields['department'].required = False

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name' , 'last_name', 'email',  'designation', 'directorate', 'department']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].required = False
        self.fields['department'].queryset = Department.objects.none()

        if 'directorate' in self.data:
            try:
                directorate_id = int(self.data.get('directorate'))
                self.fields['department'].queryset = Department.objects.filter(directorate_id=directorate_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.directorate:
            self.fields['department'].queryset = self.instance.directorate.department_set.all()
