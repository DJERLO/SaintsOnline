from django.urls import path
from userauths import views
from allauth.account.views import SignupView
from .forms import MyCustomSocialSignupForm  # Ensure the correct import of your form
app_name = "userauths"

urlpatterns = [
    path("sign-up/", views.register_view, name="sign-up"),
    path("sign-in/", views.login_view, name="sign-in"),
    path("sign-out/", views.logout_view, name="sign-out"),
    path('accounts/signup/', SignupView.as_view(form_class=MyCustomSocialSignupForm), name='account_signup'),
    path("profile/update/", views.profile_update, name="profile-update"),
]