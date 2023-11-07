from django.db import models
# from auth_app.models import Profile
from django_lifecycle import LifecycleModel, hook, AFTER_UPDATE, AFTER_SAVE

from api.static_variables import APPOINTMENT_STATUS, GENDER_CHOICES
from auth_app.models import User
from store.models import ServiceDetailsDayTime

# Create your models here.


# prof = Profile.objects.filter(status='customer')
# user = User.Profile.objects.filter(Profile=prof)
class Appointment(LifecycleModel):
    appointment_user = models.ForeignKey(
        User,           
        on_delete=models.CASCADE,
        related_name='customer_appointment',
        verbose_name='who create the appointment'
    )
    Service = models.ForeignKey(
        ServiceDetailsDayTime,
        on_delete=models.DO_NOTHING,
        verbose_name='service',
        blank=True,
        null=True
    )
    PatientName = models.CharField(max_length=200, verbose_name='patient_name')
    Age = models.IntegerField(null=False, blank=False, verbose_name='age')
    Sex = models.CharField(max_length=10, choices=GENDER_CHOICES.Gender_Choices, verbose_name='gender')
    phone = models.CharField(max_length=10)
    Status = models.CharField(
        max_length=10, choices=APPOINTMENT_STATUS.Status_Choices, verbose_name='status',
        default=APPOINTMENT_STATUS.PENDING
    )
    Rank = models.IntegerField(default=0, null=True, blank=True)
    slot_date = models.DateField(null=True, blank=True)
    time = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    payment_status=models.BooleanField(default=False)
    wallet_status=models.BooleanField(default=False)

    def __str__(self):
        # return self.appointment_user.email + "--" + str(self.Service.Time)
        return f"{self.id} - {self.Rank} "

    @hook(AFTER_SAVE, when='Status', was=APPOINTMENT_STATUS.PENDING)
    @hook(AFTER_UPDATE, when='Status', was=APPOINTMENT_STATUS.PENDING, is_now=APPOINTMENT_STATUS.ACCEPTED)
    @hook(AFTER_UPDATE, when='Status', was=APPOINTMENT_STATUS.PENDING, is_now=APPOINTMENT_STATUS.CANCELLED)
    @hook(AFTER_UPDATE, when='Status', was=APPOINTMENT_STATUS.ACCEPTED, is_now=APPOINTMENT_STATUS.PENDING)
    @hook(AFTER_UPDATE, when='Status', was=APPOINTMENT_STATUS.ACCEPTED, is_now=APPOINTMENT_STATUS.CANCELLED)
    @hook(AFTER_UPDATE, when='Status', was=APPOINTMENT_STATUS.CANCELLED, is_now=APPOINTMENT_STATUS.PENDING)
    @hook(AFTER_UPDATE, when='Status', was=APPOINTMENT_STATUS.CANCELLED, is_now=APPOINTMENT_STATUS.ACCEPTED)
    def rank_generated(self):
        if self.Status == APPOINTMENT_STATUS.PENDING:
            rank_alloted = Appointment.objects.filter(
                Status=APPOINTMENT_STATUS.PENDING,
                Service=self.Service,
                slot_date=self.slot_date,
                time=self.time
            ).count()
            if rank_alloted == 0:
                rank_alloted += 1
            else:
                Appointment.objects.filter(
                    id=self.id
                ).update(
                    Rank=rank_alloted,
                    time=self.time
                )
        if self.Status == APPOINTMENT_STATUS.ACCEPTED:
            Appointment.objects.filter(
                id=self.id,
                Service=self.Service,
                slot_date=self.slot_date,
                time=self.time
            ).update(
                Rank=self.Rank,
            )
        if self.Status == APPOINTMENT_STATUS.CANCELLED:
            data = Appointment.objects.exclude(
                Status=APPOINTMENT_STATUS.CANCELLED
            ).filter(
                slot_date=self.slot_date,
                time=self.time
            ).order_by(
                'Rank'
            )

            Appointment.objects.filter(id=self.id).update(Rank=0)

            new_ranks = []
            for index, obj in enumerate(data, start=1):
                obj.Rank = index
                new_ranks.append(obj)

            Appointment.objects.bulk_update(new_ranks, ['Rank'])


class Dummy(LifecycleModel):
    appointment_user = models.ForeignKey(
        User,           
        on_delete=models.CASCADE,
        related_name='dummy_appointment',
        verbose_name='who create the appointment'
    )
    Service = models.ForeignKey(
        ServiceDetailsDayTime,
        on_delete=models.DO_NOTHING,
        verbose_name='service',
        blank=True,
        null=True
    )
    PatientName = models.CharField(max_length=200, verbose_name='patient_name')
    Age = models.IntegerField(null=False, blank=False, verbose_name='age')
    Sex = models.CharField(max_length=10, choices=GENDER_CHOICES.Gender_Choices, verbose_name='gender')
    phone = models.CharField(max_length=10)
    Status = models.CharField(
        max_length=10, choices=APPOINTMENT_STATUS.Status_Choices, verbose_name='status',
        default=APPOINTMENT_STATUS.PENDING
    )
    Rank = models.IntegerField(default=0, null=True, blank=True)
    slot_date = models.DateField(null=True, blank=True)
    time = models.TimeField(blank=True, null=True)
    payment_status=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

class Recharge(models.Model):
    number=models.CharField(max_length=50)
    amount=models.PositiveIntegerField()
    rechargeType=models.CharField(max_length=30)
    operator=models.CharField(max_length=50)
    created_at = models.CharField(max_length=50)
    payment_status=models.BooleanField(default=False)
    wallet_status=models.BooleanField(default=False)