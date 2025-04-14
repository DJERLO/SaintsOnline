"""
URL configuration for ecomprj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static
from allauth.account.views import SignupView
from django.urls import path
from userauths.forms import MyCustomSocialSignupForm

def login_view(request):
    return redirect('account_login')

urlpatterns = [
    path('admin/login/', login_view, name='admin_login'),  # Redirect to the login view
    path('admin/', admin.site.urls),
    # Include allauth URLs for authentication
    path('accounts/', include('allauth.urls')),  # All auth URLs
    path('accounts/signup/', SignupView.as_view(form_class=MyCustomSocialSignupForm), name='account_signup'),
    path("", include("core.urls")),
    path("user/", include("userauths.urls")),
    path("useradmin/", include("useradmin.urls")),

    path("ckeditor/", include("ckeditor_uploader.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)