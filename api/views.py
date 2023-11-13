from rest_framework import viewsets,generics,status
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import Token
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.hashers import check_password
from random import randint
from datetime import timedelta,datetime
from django.utils import timezone
from django.http import HttpResponseRedirect,JsonResponse,HttpResponse
from .models import OTP
from auth_app.models import User
from customer.models import Appointment
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from .test import PhonePe
from django.urls import reverse
import hashlib,base64,requests,json
from customer.models import Appointment,Recharge
from store.models import (
    Phlebotomist,
    Shop,
    Doctor,
    Service,
    ServiceDetailsDay,
    ServiceDetailsDayTime,
    OrderService,
    Pathological_Test_Service
)
from .serializers import (
    RechargeSerializer,
    RegisterUserSerializer,
    ShopSerializer,
    DoctorSerializer,
    ServicedetailDaySerializer,
    ServicedetailDayTimeSerializer,
    ServiceSerializer,
    AppointmentSerializer,
    HomeSreenSerializer,
    PutAppointmentSerializer,
    UserSerializer,
    ClinicDoctorSerializer,
    PhlebotomistSerializer,
    OrderServiceSerializer,
    PathoOrdersSerializer,
    PathologicalTestServiceSerializer,
    AppointmentServicesSerializer,
    ShopListSerializer,
    ServiceListSerializer,
    ServiceDetailDayListTimeSerializer,
    AppointmentListSerializer,
    UserInfoSerializer,
    ChangePasswordSerializer,
    DoctorAppointmentSerializer,
    OTPSerializer,
    PaymentDataSerializer,
    PasswordSerializer,
    Userupdateserilaizer,
    AddBalanceSerializer,
    RemoveBalanceSerializer
    # CreateAppointmentSerializer
)
from .static_variables import USER_STATUS
from core import settings

# Create your views here.

class BaseClass(ModelViewSet):
    class CustomAPIException(APIException):
        status_code = 400
        default_detail = 'You are not authorized to access this endpoint'

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        data = {
            "count": len(serializer.data),
            "data": serializer.data,
        }
        return Response(data)


class UserLogin(APIView):
    http_method_names = ['post']

    def post(self, request):
        try:
            request = request.data
            user = ""
            if request:
                if request.get('email'):
                    email = request.get('email')
                    user = User.objects.filter(email=email).first()
                if request.get('mobile'):
                    mobile = request.get('mobile')
                    user = User.objects.filter(mobile=mobile).first()
                print(check_password(request.get('password'),user.password))
                if check_password(request.get('password'),user.password):
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({
                        'token': token.key,
                        'user_id': user.pk,
                        'mobile': user.mobile.national_number
                    })
                else:
                    return Response(status=400,data={"error":"invalid password"})
            else:
                return Response({
                    "email/mobile": "NULL",
                    "password": "NULL"
                })
        except Exception as err:
            return Response({
                "error": "you provided credential is not valid!!",
            })

class DoctorshopAppointmentViewSet(BaseClass):

    queryset=Appointment.objects.all()
    serializer_class=DoctorAppointmentSerializer
    def get_queryset(self):
        #newly
        doctor=self.request.data.get('doctor_id')
        clinic=self.request.data.get('clinic_id')
        if doctor and not clinic:
            try:
                doctor_obj=Doctor.objects.get(id=doctor)
                return self.queryset.filter(Service__ServiceDetailsDayID__ServiceID__Doctor=doctor_obj)
            except:
                raise self.CustomAPIExceptions() 
        if clinic and not doctor:
            try:
                clinic_obj=Shop.objects.get(id=clinic)
                return self.queryset.filter(Service__ServiceDetailsDayID__ServiceID__Clinic=clinic_obj)
            except:
                raise self.CustomAPIExceptions()
        if clinic and doctor:
            try:
                doctor_obj=Doctor.objects.get(id=doctor)
                clinic_obj=Shop.objects.get(id=clinic)
                return self.queryset.filter(Service__ServiceDetailsDayID__ServiceID__Clinic=clinic_obj,Service__ServiceDetailsDayID__ServiceID__Doctor=doctor_obj)
            except:
                raise self.CustomAPIExceptions()
        return Response({"error":"enter either clinic or doctor id"})
        #newly written

class ShopAppointmentViewSet(BaseClass):
    http_method_names = ['get']
    queryset = Appointment.objects.all()
    serializer_class = AppointmentListSerializer
    class CustomAPIExceptions(APIException):
        status_code = 400
        default_detail ='enter valid doctor name'
    def get_queryset(self):
        try:
            if self.request.user.status == USER_STATUS.SO:
                return self.queryset.filter(Service__ServiceDetailsDayID__ServiceID__Clinic__Shop_owner=self.request.user)
        except:
            raise self.CustomAPIException()


class UserAppointmentViewSet(BaseClass):
    http_method_names = ['get']
    queryset = Appointment.objects.all()
    serializer_class = AppointmentListSerializer

    def get_queryset(self):
        return self.queryset.filter(appointment_user=self.request.user.id)


class ShopViewSet(BaseClass):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_anonymous:
            if user.is_superuser:
                return self.queryset.filter(Shop_owner__status=USER_STATUS.SO)
            if self.action == 'list':
                queryset = Shop.objects.filter(Shop_owner__email=self.request.user.email)
            if self.action == 'retrieve':
                queryset = Appointment.objects.filter(appointment_user=self.request.user)
        else:
            raise self.CustomAPIException()
        return queryset

    def get_serializer(self, *args, **kwargs):
        """
        Use a custom serializer that includes nested objects.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        if self.action == 'list':
            # Use a custom serializer for list actions that includes nested objects
            serializer_class = ShopListSerializer
        if self.action == 'retrieve':
            # Use a custom serializer for retrieve actions that includes nested objects
            serializer_class = ShopListSerializer
        return serializer_class(*args, **kwargs)


class DoctorViewSet(BaseClass):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class ServiceViewSet(BaseClass):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Use a custom serializer that includes nested objects.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        if self.action == 'list':
            # Use a custom serializer for list actions that includes nested objects
            serializer_class = ServiceListSerializer
        if self.action == 'retrieve':
            # Use a custom serializer for retrieve actions that includes nested objects
            serializer_class = ServiceListSerializer
        return serializer_class(*args, **kwargs)


class ServicedetailDayViewSet(BaseClass):
    queryset = ServiceDetailsDay.objects.all()
    serializer_class = ServicedetailDaySerializer

    # def get_serializer(self, *args, **kwargs):
    #     """
    #     Use a custom serializer that includes nested objects.
    #     """
    #     serializer_class = self.get_serializer_class()
    #     kwargs['context'] = self.get_serializer_context()
    #     if self.action == 'list':
    #         # Use a custom serializer for list actions that includes nested objects
    #         serializer_class = ServicedetailListDaySerializer
    #     return serializer_class(*args, **kwargs)


class ServicedetailDayTimeViewSet(BaseClass):
    queryset = ServiceDetailsDayTime.objects.all()
    serializer_class = ServicedetailDayTimeSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Use a custom serializer that includes nested objects.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        if self.action == 'list':
            # Use a custom serializer for list actions that includes nested objects
            serializer_class = ServiceDetailDayListTimeSerializer
        if self.action == 'retrieve':
            # Use a custom serializer for retrieve actions that includes nested objects
            serializer_class = ServiceDetailDayListTimeSerializer
        return serializer_class(*args, **kwargs)


class AppointmentServicesViewset(BaseClass):
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentServicesSerializer
    queryset = ServiceDetailsDay.objects.all()
    #newly written
    class CustomAPIException(APIException):
        status_code = 400
        default_detail = 'You are not the shop owner or associated with any shop'
    class FullException(APIException):
        status_code=400
        default_detail="check doctor or clinic name again it seems there's no clinic or doctor with such name"

    def get_queryset(self):
        user = self.request.user
        doctor=self.request.data.get('doctor_id')
        Clinic=self.request.data.get('clinic_id')
        # print(service_id)
        if doctor and not Clinic:
            try:
                doctor_obj=Doctor.objects.get(id=self.request.data.get('doctor_id'))
                return ServiceDetailsDay.objects.filter(ServiceID__Doctor=doctor_obj)
            except:
                raise self.FullException()
        if Clinic and not doctor:
            try:
                clinic_obj=Shop.objects.get(id=Clinic)
                return ServiceDetailsDay.objects.filter(ServiceID__Clinic=clinic_obj)
            except:
                raise self.FullException()
        if Clinic and doctor:
            try:
                doctor_obj=Doctor.objects.get(id=doctor)
                clinic_obj=Shop.objects.get(id=Clinic)
                return ServiceDetailsDay.objects.filter(ServiceID__Clinic=clinic_obj,ServiceID__Doctor=doctor_obj)
            except:
                raise self.FullException()
        #newly written
        if user.status == USER_STATUS.SO:
            clinic = Shop.objects.get(Shop_owner =user) 
            # return ServiceDetailsDay.objects.filter(ServiceID__Clinic=user.shop_user).order_by('ServiceID')
            return ServiceDetailsDay.objects.filter(ServiceID__Clinic=clinic) #ServiceDetailsDay.objects.all()
        else:
            raise self.CustomAPIException()


class AppointmentViewSet(BaseClass):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()

    # def get_queryset(self):
    #     queryset = Appointment.objects.all()
    #     if self.action == 'list':
    #         queryset = Appointment.objects.filter(appointment_user=self.request.user)
    #     if self.action == 'retrieve':
    #         queryset = Appointment.objects.filter(appointment_user=self.request.user)
    #     return queryset

    def get_serializer(self, *args, **kwargs):
        """
        Use a custom serializer that includes nested objects.
        """
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        if self.action == 'list':
            # Use a custom serializer for list actions that includes nested objects
            serializer_class = AppointmentListSerializer
        if self.action == 'retrieve':
            # Use a custom serializer for retrieve actions that includes nested objects
            serializer_class = AppointmentListSerializer
        if self.action == 'update':
            # Use a custom serializer for update actions that includes nested objects
            serializer_class = PutAppointmentSerializer
        return serializer_class(*args, **kwargs)


class RegisterUserViewSet(BaseClass):
    http_method_names = ['post']
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = RegisterUserSerializer


class UserViewSet(BaseClass):
    http_method_names = ['get']
    queryset = User.objects.exclude(is_superuser=True)
    serializer_class = UserInfoSerializer

    class CustomAPIException(APIException):
        status_code = 400
        default_detail = 'You are not Authorized to access this endpoint'

    class payloadAPIException(APIException):
        status_code = 400
        default_detail = 'Please provide valid data'

    def get_queryset(self):

        if self.request.data:
            request = self.request.data
            if request.get('user_id') and not request.get('mobile'):
                return User.objects.exclude(is_superuser=True).filter(
                    id=request.get('user_id')
                )
            if request.get('mobile') and not request.get('user_id'):
                return User.objects.exclude(is_superuser=True).filter(
                    mobile=request.get('mobile')
                )
            if request.get('user_id') and request.get('mobile'):
                query = User.objects.exclude(is_superuser=True).filter(id=request['user_id'], mobile=request['mobile'])
                if query:
                    return query
                else:
                    raise self.payloadAPIException()
        if not self.request.user.is_anonymous:
            return User.objects.exclude(is_superuser=True)
        else:
            raise self.CustomAPIException()


# class HomeScreenViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
#     queryset = Shop.objects.all()
#     serializer_class = HomeSreenSerializer


class HomeScreenViewset(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            shop = Shop.objects.get(Shop_owner=request.user)
            serializer = HomeSreenSerializer(shop)
            return Response(serializer.data)
        except Shop.DoesNotExist:
            return Response({"error": "You are not the shop owner or associated with any shop"})


class ViewDoctorViewset(BaseClass):
    permission_classes = [IsAuthenticated]
    serializer_class = ClinicDoctorSerializer

    def get_queryset(self):
        if self.request.user.shop:
            clinic = Shop.objects.get(Shop_owner=self.request.user)
        else:
            return Service.objects.none()

        return Service.objects.filter(Clinic=clinic)


class phlebotomistViewset(BaseClass):
    permission_classes = [IsAuthenticated]
    serializer_class = PhlebotomistSerializer

    def get_queryset(self):
        return Phlebotomist.objects.filter(Shop=self.request.user.shop)


class OrderServiceViewSet(BaseClass):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderServiceSerializer

    def get_queryset(self):
        return OrderService.objects.filter(Order__complete=True, PathologicalTestService__Shop=self.request.user.shop)


class PathoOrdersViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PathoOrdersSerializer

    def get_queryset(self):
        return OrderService.objects.filter(Order__paymentDone=True,
                                           PathologicalTestService__Shop=self.request.user.shop)


class PathologicalTestServiceViewset(BaseClass):
    permission_classes = [IsAuthenticated]
    serializer_class = PathologicalTestServiceSerializer

    def get_queryset(self):
        return Pathological_Test_Service.objects.filter(Shop=self.request.user.shop)

class ChangePasswordViewSet(BaseClass):
    class nodata(APIException):
        status_code=400
        default_detail='enter password'
    class customere(APIException):
        status_code=400
        default_detail='user must be customer inorder to change password'

    @action(detail=True, methods=['patch'])
    def set_password(self, request, pk=None):
        user = User.objects.get(email=self.request.user.email)
        if user.status!='cr':
            raise self.customere()
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'status': 'password set'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileUpdateViewSet(BaseClass):
    serializer_class =UserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return User.objects.filter(email=self.request.user.email)
    @action(detail=True, methods=['patch'])
    def update_user(self, request, pk=None):
        user = User.objects.get(email=self.request.user.email)
        serializer = Userupdateserilaizer(data=request.data)
        if serializer.is_valid():
            if(serializer.validated_data['email']):
                
                user.email=serializer.validated_data['email']
            if(serializer.validated_data['age']):
                print('hello')
                user.age=serializer.validated_data['age']
            if(serializer.validated_data['gender']):
                user.gender=serializer.validated_data['gender']
            if(serializer.validated_data['mobile']):
                user.mobile=serializer.validated_data['mobile']
            if(serializer.validated_data['profile_pic']):
                user.profile_pic=serializer.validated_data['profile_pic']
            if(serializer.validated_data['city']):
                user.city=serializer.validated_data['city']
            if(serializer.validated_data['address']):
                user.address=serializer.validated_data['address']
            user.save()
            return Response({'status': 'profile updated'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OTPVerify(APIView):
    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        otp_code = request.data.get('otp_code')
        
        if mobile_number and not otp_code:
            otp_code = str(randint(100000, 999999))
            expiration_time = timezone.now() + timedelta(seconds=120)
            otp_instance= OTP.objects.create(mobile_number=mobile_number)
            otp_instance.otp_code = otp_code
            otp_instance.expiration_time = expiration_time
            otp_instance.save()
            account_sid = 'AC9619200ab617df7d99479f5d7690791f'
            auth_token = '2793b8ab7c52937beef705384ec90719'
            client = Client(account_sid, auth_token)
            message = client.messages.create(
            from_='+13348331022',
            body="Your OTP is "+otp_code+"it will expire in 2 minutes",
            to=mobile_number
            )
            return Response({'message': 'OTP generated successfully'}, status=status.HTTP_201_CREATED)
        
        elif mobile_number and otp_code:
            try:
                otp_instance = OTP.objects.get(mobile_number=mobile_number, otp_code=otp_code)
                if otp_instance.expiration_time < timezone.now():
                    return Response({'message': 'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
                otp_instance.delete()
                return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
            except OTP.DoesNotExist:
                return Response({'message': 'Invalid OTP or mobile number'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'message': 'Mobile number is required'}, status=status.HTTP_400_BAD_REQUEST)



class PaymentView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        serializer = PaymentDataSerializer(data=request.data)
        
        if serializer.is_valid():
            Appointment_id=serializer.data.get('appointment_id')
            Appointment_obj=Appointment.objects.get(pk=Appointment_id)
            x=PhonePe(merchant_id="PGTESTPAYUAT",phone_pe_salt='099eb0cd-02cf-4e2a-8aca-3e6c6aff0399',phone_pe_host='https://api-preprod.phonepe.com/apis/pg-sandbox',redirect_url='http://127.0.0.1:8000/api/payment_success',webhook_url='http://127.0.0.1:8000/api/payment_success',
                      redirect_mode= "POST")
            y=x.create_txn(order_id=str(Appointment_id),user=str(Appointment_id),amount=Appointment_obj.Service.ServiceDetailsDayID.ServiceID.Fees * 100)
            print(y)
            return Response({"deatils":y})
@csrf_exempt
def PaymentSuccess(request):
    if request.method=="POST":
        return JsonResponse(request.POST)
    return JsonResponse(request.REDIRECT)


class Rechargeviewset(viewsets.ViewSet):
    class valoper(APIException):
        status_code=400
        default_detail='please select valid operator'
    permission_classes=[IsAuthenticated]
    @action(detail=True,methods=['post'])
    @csrf_exempt
    def recharge(self,request):
        serializer=RechargeSerializer(data=request.data)
        UserID='11225'
        Token='51a0ff2d7539d8e7c9e54ea0500d7d44'
        GEOCode='77.49,27.20'
        CustomerNumber='8013791311'
        Pincode='700130'
        SPKey=''
        if serializer.is_valid():
            recharge_type=serializer.validated_data['recharge_type'].lower()
            operator=serializer.validated_data['operator'].lower()
            mob_or_dth_num=serializer.validated_data['mobile_or_dth']
            amount=serializer.validated_data['amount']
            now=datetime.now()
            current_time=now.strftime("%H:%M:%S")
            APIRequestID=str(mob_or_dth_num)+str(current_time)
            if(recharge_type=='mobile'):
                operators={
                    "airtel":'3',
                    "bsnl":'4',
                    "idea":'12',
                    "vodafone":'37',
                    "jio":'116'
                }
                if operator not in operators:
                    raise self.valoper()
                SPKey=operators[operator]
                url = "https://roundpay.net/API/TransactionAPI"
                headers = {
                    'Content-Type': 'application/json'
                }
                params={
                    'UserID': UserID,
                    'Token': Token,
                    'Account': mob_or_dth_num,
                    'Amount': amount,
                    'SPKey' :SPKey,
                    'APIRequestID': APIRequestID,
                    'GEOCode':GEOCode,
                    'CustomerNumber':CustomerNumber,
                    'Pincode':Pincode,
                    'Format':1
                }
                response_r = requests.get(url=url,headers=headers,params=params)
                now=datetime.now()
                current_time=now.strftime("%H:%M:%S")
                recharge=Recharge(number=mob_or_dth_num,amount=amount,rechargeType='mobile',operator=operator,created_at=current_time)
                recharge.save()
                print(response_r)
                if response_r.status_code==200:
                    recharge_obj=Recharge.objects.get(number=mob_or_dth_num,amount=amount,rechargeType='mobile',operator=operator,created_at=current_time)
                    recharge_obj.payment_status=True
                    recharge_obj.wallet_status=True
                    recharge_obj.save()
                    user_object=User.objects.get(email=self.request.user.email)
                    user_object.wallet_balance+=(2*amount)/100
                    user_object.save()
                    response_dict = json.loads(response_r.text) 
                    return Response(response_dict)
                else:
                    return Response({'error': 'Failed to fetch data'}, status=response_r.status_code)
            elif recharge_type=='dth':
                operators={
                    "dishtv":'53',
                    'tatasky':'55',
                    'airtel digital':'51',
                    'videocon':'56',
                    'sundirect':'54'
                }
                if operator not in operators:
                    raise self.valoper()
                SPKey=operators[operator]
                url = 'https://roundpay.net/API/TransactionAPI'
                params={
                    'UserID': UserID,
                    'Token': Token,
                    'Account': mob_or_dth_num,
                    'Amount': amount,
                    'SPKey' :SPKey,
                    'APIRequestID': APIRequestID,
                    'GEOCode':GEOCode,
                    'CustomerNumber':CustomerNumber,
                    'Pincode':Pincode,
                    'Format':1
                }
                headers = {
                    'Content-Type': 'application/json'
                }
                response_r = requests.get(url,headers=headers,params=params)
                now=datetime.datetime.now()
                current_time=now.strftime("%H:%M:%S")
                recharge=Recharge(number=mob_or_dth_num,amount=amount,rechargeType='dth',operator=operator,created_at=current_time)
                recharge.save()
                if response_r.status_code==200:
                    print(response_dict)
                    response_dict = json.loads(response_r.text) 
                    if response_dict['status'] == 1:
                        recharge.payment_status=True
                        user_object=User.objects.get(email=self.request.user.email)
                        user_object.wallet_balance+=(1*amount)/100
                        user_object.save()
                        recharge.wallet_status=True
                        recharge.save()

                    else:
                        recharge.delete()
                    return Response(response_dict)
                else:
                    return Response({'error': 'Failed to fetch data'}, status=response_r.status_code)
                

class Add_wallet_balance(viewsets.ViewSet):
    permission_classes=[IsAuthenticated]
    class customexception(APIException):
        status_code=400
        default_detail='only customers have wallet'
    @action(detail=True,methods=['post'])
    @csrf_exempt
    def add_balance(self,request):
        serializer=AddBalanceSerializer(data=request.data)
        if serializer.is_valid():
            type=serializer.validated_data['type'].lower()
            objectid=serializer.validated_data['objectid']
            user = User.objects.get(email=self.request.user.email)
            if user.status!='cr':
                raise self.customexception()
            if type=='appointment':
                obj=Appointment.objects.get(id=objectid)
                if obj.payment_status==True and obj.wallet_status==False:
                    rate=5
                    user.wallet_balance+=(rate*obj.Service.ServiceDetailsDayID.ServiceID.Fees)/100
                    user.save()
                    obj.wallet_status=True
                    obj.save()
                    return Response(status=200,data={'message':'succesfully added wallet balance'})
                elif obj.payment_status==False:
                    return Response(status=400,data={'message':'payment not succeded'})
                elif obj.wallet_status==True:
                    return Response(status=400,data={'message':'already wallet balance has been added for this'})
            obj=Recharge.objects.get(id=objectid)
            if obj.payment_status==True and obj.wallet_status==False:
                rate=1
                user.wallet_balance+=(rate*obj.amount)/100
                user.save()
                obj.wallet_status=True
                obj.save()
                return Response(status=200,data={'message':'succesfully added wallet balance'})
            elif obj.payment_status==False:
                return Response(status=400,data={'message':'payment not succeded'})
            elif obj.wallet_status==True:
                return Response(status=400,data={'message':'already wallet balance has been added for this'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            
                
class Remove_wallet_balance(viewsets.ViewSet):
    permission_classes=[IsAuthenticated]
    class customexception(APIException):
        status_code=400
        default_detail='only customers have wallet'
    @action(detail=True,methods=['post'])
    @csrf_exempt
    def remove_balance(self,request):
        serializer=RemoveBalanceSerializer(data=request.data)
        if serializer.is_valid():
            amount=serializer.validated_data['amount']
            user = User.objects.get(email=self.request.user.email)
            if user.status=='cr':
                user.wallet_balance-=amount
                user.save()
                return Response(data={"message":'removed successfully'},status=200)
            raise self.customexception()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

