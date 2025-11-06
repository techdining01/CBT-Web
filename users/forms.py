from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User



class loginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    widget = {
        'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    }

    
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'age', 'address', 'date_of_birth',
                  'role', 'gender', 'student_class', 'phone_number', 'profile_picture', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class EditUserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'age', 'address', 'date_of_birth',
                  'role', 'gender', 'student_class', 'profile_picture', 'password']        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }


class TeacherAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['subject_assigned', 'qualification', 
                  'next_of_kin', 'next_of_kin_phone', 'years_of_experience']
        exclude = ['password']
        widgets = {
            'subject_assigned': forms.Select(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'next_of_kin': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
 
    def clean_experience_years(self):
        experience_years = self.cleaned_data.get('experience_years')
        if experience_years is not None and experience_years < 0:
            raise forms.ValidationError("Experience years cannot be negative.")
        return experience_years
    

class EditTeacherAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [ 'username', 'first_name', 'last_name', 'email', 'age', 'address', 'date_of_birth',
                  'role', 'gender', 'student_class', 'profile_picture', 'subject_assigned', 'qualification', 
                  'next_of_kin', 'next_of_kin_phone', 'years_of_experience', 'password']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'subject_assigned': forms.Select(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'next_of_kin': forms.TextInput(attrs={'class': 'form-control'}),
            'next_of_kin_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'password':forms.TextInput(attrs={'class': 'form-control'}),
        }
 
    def clean_experience_years(self):
        experience_years = self.cleaned_data.get('experience_years')
        if experience_years is not None and experience_years < 0:
            raise forms.ValidationError("Experience years cannot be negative.")
        return experience_years
    
