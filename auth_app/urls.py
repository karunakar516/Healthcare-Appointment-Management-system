from .views import SignUpView, LoginView, LogoutView, otp_verify#from web
from django.urls import path,include
urlpatterns = [
        path('signup',SignUpView.as_view(),name='sign-up'),
        path('web-login',LoginView.as_view(),name='login'),
        path('logout/',LogoutView.as_view(),name='logout'),
        path('otp-verify/',otp_verify,name='otp-verify'),#from web
        ]
