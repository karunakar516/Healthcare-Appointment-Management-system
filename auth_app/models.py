import random  # from web

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.hashers import make_password
from api.static_variables import USER_STATUS, GENDER_CHOICES
from .manager import UserManager

# # Create your models here.
rand_otp = random.randint(1000, 9999)  # from web


# class Profile(models.Model):
#     user         = models.OneToOneField(User, on_delete=models.CASCADE)
#     email        = models.EmailField()
#     profile_pic  = models.ImageField(upload_to='profile_pics', blank=True, null=True)
#     phone        = models.CharField(max_length=15, blank=True)
#     status       = models.CharField(max_length=20, null=True, choices=statuses, default=statuses[0][1])
#     city         = models.CharField(max_length=50, blank=True)
#     pincode      = models.CharField(max_length=8, blank=True)

#     def __str__(self):
#         return self.user.username

# @receiver(post_save, sender = User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    is_PhoneVerified = models.BooleanField(default=False)  # from web
    is_EmailVerified = models.BooleanField(default=False)  # from web
    email_token = models.CharField(max_length=100, null=True, blank=True)
    forgot_password = models.CharField(max_length=100, null=True, blank=True)
    last_login_time = models.DateTimeField(null=True, blank=True)
    last_logout_time = models.DateTimeField(null=True, blank=True)
    wallet_balance=models.FloatField(default=float(0))
    objects = UserManager()

    age = models.IntegerField(null=True, blank=True, default=0)
    gender = models.CharField(choices=GENDER_CHOICES.Gender_Choices, max_length=6, null=True, blank=True)

    otp=models.IntegerField(null=True,)
    # extra fields
    mobile = PhoneNumberField(blank=True,unique=True)
    # otp = models.IntegerField(default=rand_otp)  # from web
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    status = models.CharField(max_length=20, choices=USER_STATUS.USER_ROLE)

    # billing address  #from web
    city = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=200, default="NULL")
    flat_name = models.CharField(max_length=200, default="NULL")
    landmark = models.CharField(max_length=200, default="NULL")
    pincode = models.CharField(max_length=8, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    

