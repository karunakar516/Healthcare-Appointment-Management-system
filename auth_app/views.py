import imp#from web
from django.shortcuts import render, redirect
from django.views import View
from . models import User
from django.contrib import messages
from django.contrib import auth#from web
from auth_app.sendMsg import sendmsg#from web
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas import ManualSchema
from api.serializers import TokenSerializer


# Create your views here.


class SignUpView(View):
    def get(self, request):
        
        return render(request, 'auth_app/sign-up.html')

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobile = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(email=email).exists():
            if password == confirm_password:
                user = User.objects.create_user(email=email, first_name=first_name, mobile=str(mobile), last_name=last_name)
                user.set_password(password)
                user.is_active=True
                user.save()
                request.session['id'] = user.id
                
            else:
                pass

            
        
        return render(request, 'auth_app/sign-up.html', context)


class LoginView(View):
    def get(self, request):
        return render(request, 'auth_app/login.html')
    
    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']

        if email and password: 

            user = auth.authenticate(email=email, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, "You have successfully logged in.")
                    return redirect('customer-home')
                messages.error(request, "You are not active user.")
                return render(request, 'auth_app/login.html')
            messages.error(request, "Invalid user.")
            return render(request, 'auth_app/login.html')
        messages.error(request, "Enter correct email and password.")
        return render(request, 'auth_app/login.html')
    
                    
class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return redirect('login')
#from web
def otp_verify(request):
    otpWritten = request.POST.get('otp')

    if not request.user.is_authenticated:
        user_id = request.session.get('id')
    else:
        user_id = request.user.id
    user = User.objects.get(id=user_id)
    
    if not request.POST:
        print(f'{user.get_full_name()} - {user.otp}')
        body = f'Hello {user.get_full_name()} your otp is {user.otp}'
        sendmsg(user.mobile, body)
        # send sms 
    if request.method == "POST":
        if int(otpWritten) == int(user.otp):
            user.is_PhoneVerified = True
            user.save()
            messages.success(request, "Phone number Verified.")
            return redirect('customer-home')
        messages.error(request, "not valid.")
        return redirect('otp-verify')

    return render(request, 'auth_app/otp_check.html')


class CustomAuthToken(ObtainAuthToken):
    serializer_class = TokenSerializer
    if coreapi is not None and coreschema is not None:
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="email",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Email",
                        description="Valid email for authentication",
                    ),
                ),
                coreapi.Field(
                    name="password",
                    required=True,
                    location='form',
                    schema=coreschema.String(
                        title="Password",
                        description="Valid password for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

obtain_auth_token = CustomAuthToken.as_view()