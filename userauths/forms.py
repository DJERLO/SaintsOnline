from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User, Profile
from allauth.account.forms import ResetPasswordKeyForm
from allauth.account.forms import SignupForm

class MyCustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def save(self):
        # Add your own processing here (e.g., logging, sending notifications, etc.)
        super(MyCustomResetPasswordKeyForm, self).save()


from django.contrib.auth.models import Group
from django import forms

class MyCustomSocialSignupForm(SignupForm):
    # Adding a field for the group selection
    def __init__(self, *args, **kwargs):
        super(MyCustomSocialSignupForm, self).__init__(*args, **kwargs)
        self.fields['group'] = forms.ChoiceField(
                            choices=[('Teacher', 'Teacher'), ('Parent', 'Parent'), ('Student', 'Student')],
                            label="Select User Group",
                            required=True,
                            widget=forms.Select(attrs={'class': 'form-select'})
    )

    # This method is called when the form is saved
    def save(self, request):
        group = self.cleaned_data.pop('group')

        user = super(MyCustomSocialSignupForm, self).save(request)

        # Ensure that the group exists in the database
        try:
            group = Group.objects.get(name=group)
        except Group.DoesNotExist:
            # If the group doesn't exist, handle it appropriately
            raise ValueError(f"Group {group} does not exist.")

        # Assign the user to the selected group
        user.groups.add(group)


        return user

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "username"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}))
    
    class Meta:
        model = User
        fields = ['username', 'email']

# Additional fields for the Profile model can be added here if needed

class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Full Name"}))
    bio = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Bio"}))
    phone = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Phone"}))

    # Use SelectMultiple widget for a normal multi-select dropdown
    relative_students = forms.ModelMultipleChoiceField(
    queryset=User.objects.filter(groups__name='Student'),)

    class Meta:
        model = Profile
        fields = ['full_name', 'image', 'bio', 'phone', 'relative_students']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        # Check if the user is a parent
        if not self.instance.user.profile.is_parent():  # Assuming the Profile is already linked to the user
            # If the user is not a parent, remove the 'relative_students' field from the form
            del self.fields['relative_students']