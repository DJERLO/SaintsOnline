from enum import unique
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100)
    bio = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to='image/')
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

        
    def save(self, *args, **kwargs):
        if self.pk:
            old_password = User.objects.get(pk=self.pk).password
            if self.password != old_password and not self.password.startswith('pbkdf2_'):
                self.set_password(self.password)
        else:
            if not self.password.startswith('pbkdf2_'):
                self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image")
    full_name = models.CharField(max_length=200, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200) # +234 (456) - 789
    address = models.CharField(max_length=200, null=True, blank=True) 
    country = models.CharField(max_length=200, null=True, blank=True) 
    
    #Parent's Details
    relative_students = models.ManyToManyField(User, blank=True, related_name='parents', symmetrical=False)

    verified = models.BooleanField(default=False)

    def is_parent(self):
        return self.user.groups.filter(name='Parent').exists()
    
    def is_student(self):
        return self.user.groups.filter(name='Student').exists()
    
    def is_teacher(self):
        return self.user.groups.filter(name='Faculty').exists() 
    
    def __str__(self):
        return f"{self.user.username} - {self.full_name} - {self.bio}"


class ContactUs(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    year = models.CharField(max_length=200)
    year = models.CharField(max_length=200)
    phone = models.CharField(max_length=200) # +63 (0912) - 3456
    subject = models.CharField(max_length=200) # +63 (0912) - 3456
    message = models.TextField()

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.full_name
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)   