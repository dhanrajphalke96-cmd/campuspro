from django import forms
from core.models import CustomUser
from .models import StaffProfile, LeaveType

class StaffUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Leave blank to keep existing password (only required for new users)."
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'address', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit role choices to staff only (exclude student)
        staff_roles = [
            ('faculty', 'Faculty'),
            ('hod', 'HOD'),
            ('principal', 'Principal'),
            ('hr', 'HR'),
            ('accountant', 'Accountant'),
            ('librarian', 'Librarian'),
            ('admin', 'Admin'),
        ]
        self.fields['role'].choices = staff_roles
        
        # If updating an existing user, password is not strictly required
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['employee_id', 'department', 'designation', 'date_of_joining', 'qualification', 'experience_years', 'specialization']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'designation': forms.Select(attrs={'class': 'form-control'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
        }


class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['name', 'max_days_per_year', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'max_days_per_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
