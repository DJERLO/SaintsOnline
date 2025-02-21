from django.contrib import admin
from userauths.models import User, ContactUs, Profile

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'bio']

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject']

class Customer(User):
    class Meta:
        proxy = True
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

class CustomerAdmin(UserAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(groups__name='Customer').exclude(groups=None).distinct()
    
    list_display = ['username', 'email']
    search_fields = ('username', 'email', 'first_name', 'last_name')


admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(Profile)