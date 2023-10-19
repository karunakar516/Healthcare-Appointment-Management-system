from django.db import models
from django.utils import timezone
# Create your models here.

class MasterConfig(models.Model):
    appointment_slot_flexibility = models.IntegerField(default=30)

    def __str__(self):
        return f" appointment_slot_flexibility : {self.appointment_slot_flexibility}"
    

class OTP(models.Model):
    mobile_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    expiration_time = models.DateTimeField(null=True, blank=True)