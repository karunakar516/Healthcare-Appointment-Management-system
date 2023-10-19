from pathlib import Path
from django.contrib import admin
from .models import Shop, Doctor, Service, ServiceDetailsDay,ServiceDetailsDayTime, Pathological_Test, Pathological_Test_Service, Phlebotomist, Order, OrderService, ShippingAddress, ServiceDetailsDayTime, Cart

# Register your models here.
admin.site.register(Shop)
admin.site.register(Doctor)
admin.site.register(Service)
admin.site.register(ServiceDetailsDay)
admin.site.register(ServiceDetailsDayTime)
admin.site.register(Pathological_Test)
admin.site.register(Pathological_Test_Service)
admin.site.register(Phlebotomist)
admin.site.register(Order)
admin.site.register(OrderService)
admin.site.register(Cart)
admin.site.register(ShippingAddress)
