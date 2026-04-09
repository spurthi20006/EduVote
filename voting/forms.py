from django import forms
from .models import Student


class SchoolLoginForm(forms.Form):
    student_id = forms.CharField(
        label='Roll Number',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. SCH-2024-001',
            'class': 'form-control',
            'id': 'id_school_student_id',
        })
    )
    class_name = forms.CharField(
        label='Class',
        max_length=20,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. 10-A',
            'class': 'form-control',
            'id': 'id_school_class_name',
        })
    )


class PULoginForm(forms.Form):
    student_id = forms.CharField(
        label='Registration Number',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. PU-2024-001',
            'class': 'form-control',
            'id': 'id_pu_student_id',
        })
    )
    year = forms.ChoiceField(
        label='Year',
        choices=[('1', '1st Year'), ('2', '2nd Year')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_pu_year',
        })
    )


class EngineeringLoginForm(forms.Form):
    student_id = forms.CharField(
        label='USN',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. 1AB21CS001',
            'class': 'form-control',
            'id': 'id_eng_student_id',
        })
    )
    branch = forms.CharField(
        label='Branch',
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. CSE',
            'class': 'form-control',
            'id': 'id_eng_branch',
        })
    )
    year = forms.ChoiceField(
        label='Year',
        choices=[('1', '1st Year'), ('2', '2nd Year'), ('3', '3rd Year'), ('4', '4th Year')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_eng_year',
        })
    )


class AdminRegistrationForm(forms.ModelForm):
    from django.contrib.auth.models import User
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(
        choices=[
            ('school', 'School Admin'),
            ('pu', 'PU College Admin'),
            ('engineering', 'Engineering College Admin'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        from django.contrib.auth.models import User
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Upload Excel File',
        help_text='Upload .xlsx file containing student data.',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx'})
    )
