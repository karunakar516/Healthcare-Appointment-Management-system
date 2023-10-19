from django import template
from store.models import ServiceDetailsDay, ServiceDetailsDayTime
from customer.models import Appointment
from datetime import datetime, timedelta, date

register = template.Library()


@register.filter(name='get_servicedetails')
def get_servicedetails(service):
    servicedet = ServiceDetailsDay.objects.filter(ServiceID=service)
    return servicedet


@register.filter(name='get_servicedetails1')
def get_servicedetails1(service):
    servicedet1 = ServiceDetailsDayTime.objects.filter(
        ServiceDetailsDayID=service)
    return servicedet1

weekdays = {
    '0': 'Monday',
    '1': 'Tuesday',
    '2': 'Wednesday',
    '3': 'Thursday',
    '4': 'Friday',
    '5': 'Saturday',
    '6': 'Sunday'
    }


@register.filter(name='get_date')
def get_date(weekday, next):
    weekday = int(weekday)
    today = datetime.today().isoweekday()
    diff = 0
    if(weekday > today):
        diff = weekday - today
    else:
        diff = 7 + weekday - today
    todayDate = date.today()
    appointment_date = todayDate + timedelta(days=diff)
    if(next == 0):
        return str(appointment_date + timedelta(days=7))
    elif(next == 1):
        return str(appointment_date + timedelta(days=14))

    return str(str(appointment_date)+','+weekdays[str(weekday)])


# @register.filter(name='get_date')
# def get_date(weekday, next):
#     weekday = int(weekday)
#     today = datetime.today().isoweekday()
#     diff = 0
#     if(weekday > today):
#         diff = weekday - today
#     else:
#         diff = 7 + weekday - today
#     todayDate = date.today()
#     appointment_date = todayDate + timedelta(days=diff)
#     if(next == 0):
#         return weekdays[str(weekday)] + ' ' + str(appointment_date + timedelta(days=7))
#     elif(next == 1):
#         return weekdays[str(weekday)] + ' ' +  str(appointment_date + timedelta(days=14))

#     return weekdays[str(weekday)] + ' ' + str(appointment_date)


