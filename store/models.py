from django.db import models
from django.db.models.signals import post_save

from api.static_variables import TIMESLOTS, SHOP_STATUS
from auth_app.models import User
from django.urls import reverse

# Create your models here.


class Shop(models.Model):
    """
    Shop : in this project shop means Shop-> Clinic
    """
    Name = models.CharField(max_length=190, unique=True)
    Shop_owner = models.OneToOneField(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name="shop_user")
    Address = models.CharField(max_length=300)
    Status = models.CharField(max_length=2, choices=SHOP_STATUS.shop_status, default=SHOP_STATUS.E)
    Interior_image = models.ImageField(
        upload_to='shops', blank=True, null=True)
    OffDay = models.CharField(max_length=10, default=TIMESLOTS.SUNDAY, choices=TIMESLOTS.week_days)
    Image = models.ImageField(upload_to='shops', blank=True, null=True)
    Opening_time = models.TimeField(null=True, blank=True)
    Closing_time = models.TimeField(null=True, blank=True)
    Shop_url = models.URLField(
        max_length=200, default='www.watduwant.com/show_details')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        details_url = f"127.0.0.1:8000/show_details/{self.pk}"
        self.Shop_url = details_url
        super().save(*args, **kwargs)
    def __str__(self):
        return self.Name



class Pathological_Test(models.Model):
    TestName = models.CharField(max_length=100)
    Desc = models.TextField()
    Image = models.ImageField(upload_to='shops', blank=True, null=True)
    SampleType = models.CharField(max_length=100)
    FastingRequirement = models.BooleanField(default=False)

    def __str__(self):
        return self.TestName


class Pathological_Test_Service(models.Model):
    Shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="PathologicalTestServices")
    Tests = models.ForeignKey(Pathological_Test, on_delete=models.CASCADE, related_name="PathologicalTestServices")
    Price = models.IntegerField()
    ReportDeliveryTime = models.TimeField()

    def __str__(self):
        return f"{str(self.Shop)} - {str(self.Tests)}"


class Doctor(models.Model):
    Name = models.CharField(max_length=100, unique=True)
    Specialization = models.CharField(max_length=200, blank=False)
    Experience = models.IntegerField()
    Image = models.ImageField(upload_to='doctors', blank=True, null=True)

    def __str__(self):
        return self.Name


class Phlebotomist(models.Model):
    Shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="Phlebotomists")
    Name = models.CharField(max_length=100)
    PhoneNumber = models.CharField(max_length=15)

    def __str__(self):
        return self.Name


class Order(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="order")
    DateOrdered = models.DateField(null=True, blank=True, auto_now=True)
    complete = models.BooleanField(default=False)
    paymentDone = models.BooleanField(default=False)
    transactionId = models.CharField(max_length=12, null=True, blank=True)
    total_price = models.FloatField(default=0)
    
    def __str__(self):
        return str(self.user) + " - Order"


class Cart(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name="cart")
    total_price = models.FloatField(default=0)

    def __str__(self):
        return str(self.user) + " - Cart"


status_choices = [
    ('0', 'Not assigned'),
    ('1', 'Assigned'),
    ('2', 'delivered'),
    ('3', 'Not Delivered'),
    ('4', 'Collected'),
    ('5', 'Not Collected')
]


class OrderService(models.Model):
    Order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orderServices", null=True, blank=True)
    Cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="orderServices", null=True, blank=True)
    PathologicalTestService = models.ForeignKey(Pathological_Test_Service, on_delete=models.CASCADE,
                                                related_name="orderServices")
    DateAdded = models.DateField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=1, choices=status_choices, default='0')
    collected_date = models.DateField(null=True)
    report = models.FileField(upload_to='reports', null=True, blank=True)

    def __str__(self):
        return str(self.Cart) + " - " + str(self.quantity)


Gender_Choices = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
)


class ShippingAddress(models.Model):
    User = models.OneToOneField(User, on_delete=models.CASCADE, related_name="shippingAddress")
    # patientName = models.CharField(max_length=100)
    # age = models.IntegerField()
    # gender = models.CharField(choices=Gender_Choices, max_length=5)
    FlatName = models.CharField(max_length=200)
    StreetName = models.CharField(max_length=200)
    pincode = models.CharField(max_length=10)
    AddressType = models.CharField(max_length=200)
    MobileNumber = models.CharField(max_length=15)
    AppointmentDate = models.DateField()
    AppointmentTimeSlot = models.TimeField()

    def __str__(self):
        return self.User + " - " + self.patientName


class Service(models.Model):
    Clinic = models.ForeignKey(
        Shop, on_delete=models.CASCADE, null=True, blank=True, related_name="services")
    Doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, null=True, blank=True, related_name='services')
    Fees = models.IntegerField()

    class Meta:
        unique_together = (('Clinic', 'Doctor'),)

    @property
    def get_name(self):
        return f"{self.Clinic} - {self.Doctor}"

    def __str__(self):
        return self.get_name


class ServiceDetailsDay(models.Model):
    ServiceID = models.ForeignKey(
        Service, on_delete=models.CASCADE, null=True, blank=True, related_name='serviceDetailsDays')
    Day = models.CharField(max_length=10, choices=TIMESLOTS.week_days, null=True)

    class Meta:
        unique_together = (('ServiceID', 'Day'),)

    @property
    def get_name_day(self):
        return self.ServiceID.get_name + "--" + str(self.Day)

    def __str__(self):
        return self.get_name_day


class ServiceDetailsDayTime(models.Model):
    ServiceDetailsDayID = models.ForeignKey(
        ServiceDetailsDay,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='serviceDetailsDayTimes')
    Time = models.TimeField()
    Visit_capacity = models.IntegerField()

    class Meta:
        unique_together = (('ServiceDetailsDayID', 'Time'),)
 
    @property
    def serviceID(self):
        return self.ServiceDetailsDayID.ServiceID.id
    
    @property
    def cinicName(self):
        return self.ServiceDetailsDayID.ServiceID.Clinic.Name
    
    @property
    def cinicID(self):
        return self.ServiceDetailsDayID.ServiceID.Clinic.id
    @property
    def doctorName(self):
        return self.ServiceDetailsDayID.ServiceID.Doctor.Name
    
    @property
    def doctorID(self):
        return self.ServiceDetailsDayID.ServiceID.Doctor.id
    
    
    @property
    def serviceDay(self):
        return self.ServiceDetailsDayID.Day

    def __str__(self):
        return self.ServiceDetailsDayID.get_name_day + "" + str(self.Time)+"-"+str(self.id)


def create_cart(sender, instance, created, *args, **kwargs):
    user = instance
    if created:
        Cart.objects.create(user=user)


def save_user_profile(sender, instance, **kwargs):
    instance.cart.save()


post_save.connect(create_cart, sender=User)
post_save.connect(save_user_profile, sender=User)

'''
***
###


    - Add field day to servicedetails
    - Alter unique_together for service (1 constraint(s))       
    - Alter unique_together for servicedetails (1 constraint(s))
    - Remove field day from service
    - Remove field Time from servicedetails
    - Remove field Visit_capacity from servicedetails
    - Create model ServiceDetails1
###



Migrations for 'store':
  store\migrations\0022_auto_20211024_1244.py
    - Create model ServiceDetailsDay
    - Rename field closing_time on shop to Closing_time
    - Rename field Integer_image on shop to Interior_image
    - Rename field offDay on shop to OffDay
    - Rename field opening_time on shop to Opening_time
    - Rename field shop_owner on shop to Shop_owner
    - Rename field shop_url on shop to Shop_url
    - Rename model ServiceDetails1 to ServiceDetailsDayTime
    - Delete model ServiceDetails
    - Add field ServiceDetailsDayID to servicedetailsdaytime
    - Alter unique_together for servicedetailsdaytime (1 constraint(s))
    - Remove field ServiceDetailsID from servicedetailsdaytime

***////
'''