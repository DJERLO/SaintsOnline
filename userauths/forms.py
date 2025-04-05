from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User, Profile
from allauth.account.forms import ResetPasswordKeyForm

class MyCustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def save(self):
        # Add your own processing here (e.g., logging, sending notifications, etc.)
        super(MyCustomResetPasswordKeyForm, self).save()

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "username"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}))
    
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Full Name"}))
    bio = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Bio"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Phone"}))

    class Meta:
        model = Profile
        fields = ['full_name', 'image', 'bio', 'phone']