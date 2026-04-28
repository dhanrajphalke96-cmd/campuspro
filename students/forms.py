from django import forms
from .models import StudentProfile

class StudentFilterForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'}))
    department = forms.IntegerField(required=False)
    semester = forms.IntegerField(required=False)
