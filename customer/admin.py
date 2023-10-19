from django.contrib import admin

from .models import Appointment


# Register your models here.
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Appointment._meta.get_fields()]


admin.site.register(Appointment, AppointmentAdmin)
