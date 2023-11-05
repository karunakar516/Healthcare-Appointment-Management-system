from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ShopViewSet, UserViewSet, DoctorViewSet, ServiceViewSet, ServicedetailDayViewSet, \
    ServicedetailDayTimeViewSet, HomeScreenViewset, ViewDoctorViewset, phlebotomistViewset, \
    OrderServiceViewSet, PathoOrdersViewSet, PathologicalTestServiceViewset, AppointmentServicesViewset, \
    RegisterUserViewSet, UserLogin, ShopAppointmentViewSet, UserAppointmentViewSet, ChangePasswordViewSet,\
    UserProfileUpdateViewSet,AppointmentViewSet,DoctorshopAppointmentViewSet,OTPVerify,PaymentView,PaymentSuccess,Recharge
app_name='api'
router = DefaultRouter()
router.register('shops', ShopViewSet, basename='shops')
router.register('shopAppointmentHistory', ShopAppointmentViewSet, basename='appointment_based_on_shops')
router.register('userAppointmentHistory', UserAppointmentViewSet, basename='appointment_based_on_user')
router.register('doclincApoointmentHistory',DoctorshopAppointmentViewSet,basename='appointment_based_on_clinic_and _doctor')
# router.register('profiles', ProfileViewSet, basename='profiles')
router.register('register', RegisterUserViewSet, basename='register_users')
router.register('profile360', UserViewSet, basename='users')
router.register('doctors', DoctorViewSet, basename='doctors')
router.register('services', ServiceViewSet, basename='services')
router.register('servicedetailsday', ServicedetailDayViewSet, basename='servicedetailsday')
router.register('viewdoctors', ViewDoctorViewset, basename='view-doctors')
# router.register('home', HomeScreenViewset, basename='homescreen')
router.register('servicedetailsdaytime', ServicedetailDayTimeViewSet, basename='servicedetailsdaytime')
router.register('appointments', AppointmentViewSet, basename='appointment')
router.register('appointment_services', AppointmentServicesViewset, basename='appointment-services')
router.register('phlebotomist', phlebotomistViewset, basename='phlebotomist')
router.register('order-services', OrderServiceViewSet, basename='order-services')
router.register('patho-orders', PathoOrdersViewSet, basename='patho-orders')
router.register('pathoTests', PathologicalTestServiceViewset, basename='pathoTests')
# router.register('profileupdate',UserProfileUpdateViewSet,basename='user')
# router.register('password-change',ChangePasswordViewSet,basename='changepass')


urlpatterns = [
    path('', include(router.urls)),
    path('login', UserLogin.as_view()),
    # path('passwordreset',ChangePasswordView.as_view(),name='password-reset'),
    path('home/', HomeScreenViewset.as_view(), name="homescreen"),
    # path('appointments/', AppointmentCreateView.as_view(), name='appointment-create'),
    path('recharge',Recharge.as_view({'post':'recharge'}),name='recharge'),
    path('otp-verify',OTPVerify.as_view(),name='otp'),
    path('payment',PaymentView.as_view(),name='payment'),
    path('profileupdate',UserProfileUpdateViewSet.as_view({'patch':'update_user'}),name='user_update'),
    path('change_password', ChangePasswordViewSet.as_view({'patch': 'set_password'}), name='change_password'),
    path('payment_success',PaymentSuccess,name='paysuc'),
    #  path('dj-rest-auth/', include('dj_rest_auth.urls')),
    #  path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
]
