import datetime
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_writable_nested import WritableNestedModelSerializer
from phonenumber_field.formfields import PhoneNumberField
from rest_framework import serializers,status
from rest_framework.authtoken.views import Token
from rest_framework.serializers import ModelSerializer
from rest_framework.response import Response
from api.helpers import GetServiceSlot
from api.static_variables import USER_STATUS,GENDER_CHOICES 
from auth_app.models import User
from customer.models import Appointment
from store.models import Shop, Doctor, Service, ServiceDetailsDay, ServiceDetailsDayTime, Phlebotomist, OrderService, \
    Pathological_Test_Service
from .models import OTP

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id', 'Name', 'Experience', 'Specialization', 'Image']


class ServicedetailDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDetailsDay
        fields = ['id', 'ServiceID', 'Day']


class ServiceDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDetailsDay
        fields = ['Day']


class ServicedetailDayTimeSerializer(serializers.ModelSerializer):
    doctorID   = ServiceDetailsDayTime.doctorID
    class Meta:
        model = ServiceDetailsDayTime
        fields = ['id', 'ServiceDetailsDayID','doctorID', 'Time', 'Visit_capacity']


class ServiceDetailDayListTimeSerializer(serializers.ModelSerializer):
    serviceDay   = ServiceDetailsDayTime.serviceDay
    serviceID           = ServiceDetailsDayTime.serviceID
    cinicName           = ServiceDetailsDayTime.cinicName
    doctorName          = ServiceDetailsDayTime.doctorName
    cinicID             = ServiceDetailsDayTime.cinicID
    doctorID            = ServiceDetailsDayTime.doctorID

    class Meta:
        model = ServiceDetailsDayTime
        fields = ['id','cinicID','doctorID','serviceID', 'ServiceDetailsDayID','cinicName','doctorName','serviceDay', 'Time', 'Visit_capacity']


class PutAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['Status']


class OrderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderService
        fields = '__all__'


class PathoOrdersSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='Order__user')
    contact = serializers.CharField(source='Order__user__shippingAddress__MobileNumber')
    date = serializers.DateField(source='DateAdded')
    location = serializers.SerializerMethodField()
    Test = serializers.CharField(source='PathologicalTestService__Tests')

    class Meta:
        model = OrderService
        fields = ['name', 'contact', 'location', 'status', 'report', 'collected_date', 'Test', 'date']

    def get_location(self, obj):
        address = obj.Order.user.shippingAddress
        return f'{address.FlatName}, {address.StreetName}, {address.AddressType}, {address.pincode}'


class PathologicalTestServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathological_Test_Service
        fields = '__all__'


class ShopSerializer(ModelSerializer):

    @transaction.atomic
    def validate(self, attrs):
        userid = self.context.get('request').data.get('Shop_owner')
        user = User.objects.get(id=userid)

        if user.status == USER_STATUS.CR:
            raise serializers.ValidationError(
                {"error": f"{user.email} is not Shop Owner"}
            )
        return attrs

    class Meta:
        model = Shop
        fields = ['id', 'Name', 'Shop_owner', 'Address', 'Status', 'OffDay', 'Interior_image', 'Image', 'Opening_time',
                  'Closing_time', 'Shop_url']


class UserInfoSerializer(serializers.ModelSerializer):
    shop = serializers.SerializerMethodField()

    def get_shop(self, obj):
        shop_queryset = Shop.objects.filter(Shop_owner=obj)
        shop_serializer = ShopSerializer(instance=shop_queryset, many=True)
        return shop_serializer.data

    class Meta:
        model = User
        fields = ['id', 'email', 'age', 'gender', 'mobile', 'profile_pic', 'status', 'city', 'address', 'shop']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'age', 'gender', 'mobile', 'profile_pic', 'status', 'city', 'address']

class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True, min_length=8)

class Userupdateserilaizer(serializers.Serializer):
    email=serializers.EmailField(required=False,default=None)
    age=serializers.IntegerField(required=False,default=0)
    gender=serializers.CharField(required=False,default=None)
    mobile=serializers.IntegerField(required=False,default=None)
    profile_pic=serializers.ImageField(required=False,default=None)
    city=serializers.CharField(required=False,default=None)
    address=serializers.CharField(required=False,default=None)


class RegisterUserSerializer(serializers.ModelSerializer):
    number = PhoneNumberField(region="IN")
    age = serializers.IntegerField(required=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'profile_pic', 'mobile', 'status', 'city', 'pincode', 'age', 'gender', 'address'
        ]

        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class ShopListSerializer(ModelSerializer):
    Shop_owner = UserInfoSerializer(read_only=True)

    class Meta:
        model = Shop
        fields = ['id', 'Name', 'Shop_owner', 'Address', 'Status', 'OffDay', 'Interior_image', 'Image', 'Opening_time',
                  'Closing_time', 'Shop_url']


# class ServiceSerializer(ModelSerializer):
#
#     Clinic = ShopSerializer()
#     Doctor = DoctorSerializer()
#     class Meta:
#         model = Service
#         fields = ['id', 'Clinic', 'Doctor', 'Fees']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'Clinic', 'Doctor', 'Fees']


class ServiceListSerializer(serializers.ModelSerializer):
    Clinic = ShopListSerializer(read_only=True)
    Doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'Clinic', 'Doctor', 'Fees']


class GetDoctorSerializer(serializers.ModelSerializer):
    Doctor = DoctorSerializer(read_only=True)
    timing = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Service
        fields = ['Doctor', 'timing']

    def get_timing(self, obj):
        try:
            service = ServiceDetailsDay.objects.get(ServiceID=obj, Day=str(datetime.datetime.today().isoweekday()))
            return ServicedetailDayTimeSerializer(service.serviceDetailsDayTimes.all(), many=True).data

        except ServiceDetailsDay.DoesNotExist:
            return None


# class ViewDoctorSerializer(serializers.ModelSerializer):
#     class Meta:


class HomeSreenSerializer(serializers.ModelSerializer):
    doctors = serializers.SerializerMethodField()
    shop_owner = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    mobile = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ['id', 'Name', 'user_id', 'shop_owner', 'Image', 'Interior_image', 'Address', 'Status', 'Shop_url',
                  'Opening_time', 'Closing_time', 'doctors', 'Status', 'OffDay', 'mobile']

    def get_mobile(self, obj):
        return obj.Shop_owner.mobile

    def get_user_id(self, obj):
        return obj.Shop_owner.id

    def get_shop_owner(self, obj):
        return obj.Shop_owner.email

    def get_doctors(self, obj):
        return GetDoctorSerializer(obj.services.all(), many=True).data


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password", ),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class PutDoctorSerializer(serializers.ModelSerializer):
    visit_days = serializers.SerializerMethodField()
    timings = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = ['visit_days', 'timings']

    def get_timings(self, obj):
        queryset = ServiceDetailsDayTime.objects.filter(ServiceDetailsDayID__ServiceID=obj)
        return ServicedetailDayTimeSerializer(queryset, many=True)

    def get_visit_days(self, obj):
        return ServiceDaysSerializer(obj.serviceDetailsDays.all(), many=True).data


class visitdaysSerializer(serializers.ModelSerializer):
    serviceDetailsDayTimes = ServicedetailDayTimeSerializer(many=True)

    class Meta:
        model = ServiceDetailsDay
        fields = ['id', 'Day', 'serviceDetailsDayTimes']


class PhlebotomistTestsSerializer(serializers.ModelSerializer):
    test = serializers.CharField(source='PathologicalTestService__Tests')
    cost = serializers.CharField(source='PathologicalTestService__Price')

    class Meta:
        model = OrderService
        fields = ['test', 'price']


class PhlebotomistSerializer(serializers.ModelSerializer):
    test = serializers.SerializerMethodField()

    class Meta:
        model = Phlebotomist
        fields = ['id', 'Name', 'PhoneNumber', 'test']

    def get_test(self, obj):
        return PhlebotomistTestsSerializer(
            OrderService.objects.filter(PathologicalTestService__Shop=obj.Shop, Order__paymentDone=True),
            many=True).data


class ClinicDoctorSerializer(serializers.ModelSerializer):
    Doctor = serializers.SerializerMethodField()
    serviceDetailsDays = visitdaysSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'Doctor', 'Fees', 'serviceDetailsDays']

    def get_Doctor(self, obj):
        return DoctorSerializer(obj.Doctor).data

    def update(self, instance, validated_data):
        visit_days_data = validated_data.pop('serviceDetailsDays')
        visit_days = (instance.serviceDetailsDays).all()
        visit_days = list(visit_days)
        instance.Fees = validated_data.get('Fees', instance.Fees)
        instance.save()

        for visit_day_data in visit_days_data:
            visit_day = visit_days.pop(0)
            visit_day.Day = visit_day_data.get('Day', visit_day.Day)
            timings = visit_day.serviceDetailsDayTimes.all()
            timings = list(timings)
            timings_data = visit_day_data.pop('serviceDetailsDayTimes')
            for timing_data in timings_data:
                timing = timings.pop(0)
                timing.Time = timing_data.get('Time', timing.Time)
                timing.Visit_capacity = timing_data.get('Visit_capacity', timing.Visit_capacity)
                timing.save()

            visit_day.save()

        return instance


class AppointmentServicesSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(source='ServiceID.Doctor')
    timing = ServicedetailDayTimeSerializer(source='serviceDetailsDayTimes', many=True)
    class Meta:
        model = ServiceDetailsDay
        depth = 1
        fields = ['id', 'Day', 'timing', 'doctor']


class AppointmentSerializer(WritableNestedModelSerializer):
    doctor = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    user_data = serializers.DictField(allow_null=True, required=False)
    slot_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d'])
    user_code = serializers.CharField(
        source='appointment_user',
        required=False
    )

    @transaction.atomic
    def validate(self, attrs):
        requests = self.context.get('request')
        slot = GetServiceSlot() 
        token_user = requests.user
        slot_date = requests.data.get('slot_date')
        slot_date_obj = slot.string_date_to_date(slot_date)
        open_day = slot.slot_flexibility(slot_date_obj)
        if datetime.datetime.now().date().month > open_day.month:
            raise serializers.ValidationError(
                {"error": "Please provide valid slot date information. it's future month date"}
            )
        if datetime.datetime.now().month > slot_date_obj.month:
            raise serializers.ValidationError(
                {"error": "Please provide valid slot date information. it's past month date"}
            )
        if slot_date_obj < datetime.datetime.now().date():
            raise serializers.ValidationError(
                {"error": "Please provide valid slot date information. it's past month or date"}
            )
        if token_user.status == USER_STATUS.SO and not requests.data.get('user_data'):
            raise serializers.ValidationError(
                {"error": "Please provide user information."}
            )
        if token_user.status == USER_STATUS.CR and requests.data.get('user_data'):
            raise serializers.ValidationError(
                {"error": "Please Don't added any extra stuff."}
            )

        else:
            attrs['token_user'] = token_user

        service = requests.data.get('Service')
        slot_status, slot_date_list = slot.process(slot_date, service)
        if not slot_status:
            raise serializers.ValidationError(
                {"error": f"Invalid slot date. Please choose a valid date from this {slot_date_list}"}
            )
        return attrs

    def create(self, validated_data):
        appointment_user = None
        if validated_data.get('user_data'):
            user_data = validated_data.pop('user_data')
            if user_data:
                existing_user = User.objects.filter(mobile=user_data.get('mobile')).first()
                print(existing_user)
                validated_data.pop('token_user')
                if existing_user:
                    appointment_user = existing_user
                    print('exists')
                else:
                    user_serializer = UserInfoSerializer(data=user_data)
                    if user_serializer.is_valid():
                        user = user_serializer.save()
                        userx=User.objects.filter(mobile=user_data.get('mobile')).first()
                        userx.set_password(user_data.get('password'))
                        userx.save()
                        Token.objects.create(user=userx)
                        appointment_user = user
                    else:
                        print('hello')
                        errors = user_serializer.errors
                        errors['mobile'] = ["User data not found"]
                        raise serializers.ValidationError(
                            {"user_data": errors}
                        )
                    if user:
                        print("user create")
        else:
            appointment_user = validated_data.pop('token_user')

        service_details_day_time = ServiceDetailsDayTime.objects.filter(id=validated_data.get('Service').id).first()
        if service_details_day_time:
            validated_data['time'] = service_details_day_time.Time
        else:
            validated_data['time'] = datetime.datetime.now().time()
        validated_data['appointment_user'] = appointment_user
        instance = Appointment.objects.create(**validated_data)
        return instance

    class Meta:
        model = Appointment
        fields = [
            'id', 'user_code', 'user_data', 'slot_date',
            'Service', 'PatientName', 'Age',
            'Sex', 'phone', 'Status',
            'time', 'doctor'
        ]

    def get_doctor(self, obj):
        return DoctorSerializer(obj.Service.ServiceDetailsDayID.ServiceID.Doctor).data

    def get_time(self, obj):
        return ServicedetailDayTimeSerializer(obj.Service).data


class AppointmentListSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    Service = ServicedetailDayTimeSerializer(read_only=True)
    appointment_user = UserInfoSerializer(read_only=True)
    class Meta:
        model = Appointment
        fields = '__all__'

class DoctorAppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    Service = ServicedetailDayTimeSerializer(read_only=True)
    appointment_user = UserInfoSerializer(read_only=True)
    doctor_id=serializers.CharField(required=False)
    clinic_id=serializers.CharField(required=False)
    class Meta:
        model= Appointment
        fields= '__all__'

class UserSerialize(serializers.ModelSerializer):
    password=serializers.CharField()
    class Meta:
        model = User
        fields = ('password','email')
from rest_framework import serializers

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data.get('old_password')
            if user.status=='cr':
                if user.check_password(old_password):
                    new_password = serializer.validated_data.get('new_password')
                    user.set_password(new_password)
                    user.save()
                    return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'old_password': ['Incorrect password.']}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error':'should only be customer'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = '__all__'

class PaymentDataSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField()
