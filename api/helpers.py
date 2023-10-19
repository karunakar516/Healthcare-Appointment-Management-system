from datetime import datetime, timedelta

from rest_framework import serializers

from api.models import MasterConfig
from store.models import ServiceDetailsDayTime


class GetServiceSlot(object):
    @staticmethod
    def slot_flexibility(slot_date):
        master_object = None
        try:
            master_object = MasterConfig.objects.last()
            master_object = master_object.appointment_slot_flexibility
            open_day = slot_date + timedelta(master_object)
            return open_day
        except Exception:
            if not master_object:
                raise serializers.ValidationError(
                    {"error": f"Exception from {__class__.__module__} and error is : Create MasterObject in Database"}
                )
            raise serializers.ValidationError(
                {"error": f"Exception from {__class__.__module__}"}
            )

    @staticmethod
    def service_data(service_id):
        return ServiceDetailsDayTime.objects.get(id=service_id)

    @staticmethod
    def check_slot(date, slot_date_list):
        if str(date) in slot_date_list:
            slot_booked = True
        else:
            slot_booked = False
        return slot_booked, slot_date_list

    @staticmethod
    def string_date_to_date(date):
        """
        please provide date string only,
        provide date format like '%Y-%m-%d'
        """
        return datetime.strptime(date, '%Y-%m-%d').date()

    def process(self, slot_date, service):
        date = self.string_date_to_date(slot_date)
        open_day = self.slot_flexibility(date)
        slot_date_list = []
        weekday = self.service_data(service).ServiceDetailsDayID.Day
        delta = timedelta(days=1)
        tempDate = date
        while tempDate <= open_day:
            if tempDate.weekday() == int(weekday):
                slot_date_list.append(
                    tempDate.strftime(
                        "%Y-%m-%d"
                    )
                )
            tempDate += delta
        return self.check_slot(date, slot_date_list)
