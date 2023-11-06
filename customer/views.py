from ast import Try
from auth_app.models import User
from django.contrib.auth.decorators import login_required
from store.models import ServiceDetailsDay, Shop, ServiceDetailsDayTime, Service, Doctor, OrderService, Pathological_Test_Service, Cart, Order
from django.shortcuts import render, redirect
from .models import Appointment,Dummy,Recharge
from django.contrib import messages
import datetime
import json,requests
import razorpay
from django.views.decorators.csrf import csrf_exempt
from .templatetags.custom_tags import get_date
from api.test import PhonePe
from django.http import HttpResponseRedirect
from django.urls import reverse
import base64
from PIL import Image
from io import BytesIO

# Create your views here.
import os
def home(request):
    shops = Shop.objects.all()
    today = datetime.datetime.today().weekday()

    if request.method == "POST":
        searched = request.POST['searched']

        searches = Doctor.objects.filter(Name__icontains=searched)
        search = Shop.objects.filter(Name__icontains=searched)

        return render(request, 'customer/index.html',
                      {'shops': shops, 'today': today, 'searched': searched, 'searches': searches, 'search': search, })

    else:
        return render(request, 'customer/index.html', {'shops': shops, 'today': today})


def showCart(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    price = 0
    for item in cart.orderServices.all():
        price += item.PathologicalTestService.Price*item.quantity
    cart.total_price = price
    cart.save()
    id = 1
    for item in cart.orderServices.all():
        id = item.id
    
    client = razorpay.Client(auth=("rzp_test_wjZAp6QdWONwih", "VWWSovCkW3DMdqs1tkLm70tx"))
    if price == 0: 
        price = 1
    DATA = {
        "amount": price*100,
        "currency": "INR",
        "payment_capture": "1",
        # "receipt": "receipt#1",
        # "notes": {
        #     "key1": "value3",
        #     "key2": "value2"
        # }
    }
    # client.order.create(data=DATA)
    payment = client.order.create(data=DATA)

    return render(request, "customer/cart.html", {'cart': cart, 'user': request.user, 'payment': payment, 'amount': price*100})


def btnchk(request):
    if request.user.is_authenticated:
        return render(request, 'customer/index.html')
    else:
        return render(request, 'sign-up.html')


@login_required(login_url='login')
def account(request):
    profile = User.objects.get(id=request.user.id)
    appointments = Appointment.objects.filter(appointment_user=request.user)
    return render(request, 'customer/account.html', {'profile': profile, 'appointments': appointments})


def show_details(request, shop_id):
    details = Shop.objects.get(pk=shop_id)
    data = Service.objects.filter(Clinic=details) 
    # data1 = ServiceDetailsDayTime.objects.get(pk=ServiceDetailsDayID)
    # data1 = ServiceDetailsDayTime.objects.all().select_related("ServiceDetailsDay")

    return render(request, 'clinicalldetails.html', {'details': details, 'data': data, 'n':range(2)})

def serviceTime(request):
    dayID = request.GET.get("dayId");
    serviceTimes = ServiceDetailsDay.objects.get(id=dayID).serviceDetailsDayTimes.all
    # serviceTimes = serviceTimes.serviceDetailsDayTimes.all()
    return render(request, 'serviceTimeDropdown.html', {'serviceTimes': serviceTimes})


def appointment(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            customer = request.user
            service_pk = request.POST.get("service_pk")
            service = Service.objects.get(pk=service_pk)
            patient_name = request.POST.get("patient_name")
            print(patient_name)
            shop_id = service.Clinic.id
            age = request.POST.get("age")
            print(age)
            phone = request.POST.get("phone")
            sex = request.POST.get("sex")
            # date = request.POST.get("date").split(",")
            # datefm = datetime.date(int(date[2]), int(date[1]), int(date[0]))
            #day = request.POST.get("days")
            timelist = request.POST.get("Time").split(",")
            print(timelist)

            days = get_date(request.POST.get("days"),2).split(",")
            print(days)
            date = days[0]
            day = request.POST.get("days")
            
            time = timelist[0]
            time2 = timelist[1]
            status = "P"
            time2 = datetime.datetime.strptime(time2, '%H:%M:%S').time()
            print(day)
            serviceday = ServiceDetailsDay.objects.get(Day=day, ServiceID=service_pk)
            servicedetaildaytime = ServiceDetailsDayTime.objects.get(ServiceDetailsDayID=serviceday, Time=time2)
            slots = ServiceDetailsDayTime.objects.get(
                ServiceDetailsDayID=serviceday, Time=time2).Visit_capacity
            Nslots = Appointment.objects.filter(Status="P", Service=servicedetaildaytime, slot_date=date).count() + Appointment.objects.filter(Status="A", Service=servicedetaildaytime, slot_date=date).count()

            if(Nslots+1 > slots):
                messages.error(
                    request, "No slots are available on that date. Please choose a different date!!")
                return redirect(f'../show_details/{shop_id}')
            appointment=Dummy(appointment_user=customer,Service=servicedetaildaytime, PatientName=patient_name,
                                      Age=age, Sex=sex, Status=status, phone=phone, slot_date=date)
            appointment.save()
            oid=Dummy.objects.filter(appointment_user=customer,Service=servicedetaildaytime, PatientName=patient_name,
                                      Age=age, Sex=sex, Status=status, phone=phone, slot_date=date).first()
            x=PhonePe(merchant_id="PGTESTPAYUAT",phone_pe_salt='099eb0cd-02cf-4e2a-8aca-3e6c6aff0399',phone_pe_host='https://api-preprod.phonepe.com/apis/pg-sandbox',redirect_url='https://watduwant.onrender.com/paymenthandle/',webhook_url='https://watduwant.onrender.com/paymenthandle/',
                      redirect_mode= "POST")
            y=x.create_txn(order_id=str(oid.id),user=str(oid.id),amount=service.Fees * 100)
            print(y)
            return redirect(y['data']['instrumentResponse']['redirectInfo']['url'])
            
        messages.error(request, "Fill the appointment form correctly.")
        return redirect("customer-home")
    messages.error(request, "You must login to book an appointment.")
    return redirect("customer-home")


def BookPathologicalService(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            user = request.user
            patient_name = request.POST['patient_name']
            age = request.POST.get("age")
            phone = request.POST.get("phone")
            sex = request.POST.get("sex")
            pathological_pk = request.POST["pathological_pk"]
            pathologicalTestService = Pathological_Test_Service.objects.get(id=pathological_pk)
            shop_id = pathologicalTestService.Shop.id
            cart = Cart.objects.get(user=user)
            orderService = OrderService(Cart=user.cart, PathologicalTestService=pathologicalTestService)
            orderService.save()
            cart.total_price =  cart.total_price + pathologicalTestService.Price*orderService.quantity
            cart.save()

            messages.success(
                request, "Your request has been received and we'll notify you shortly about the confirmation.")
            return redirect(f'../show_details/{shop_id}')
        messages.error(request, "Fill the booking form correctly.")
        return redirect("customer-home")
    messages.error(request, "You must login to book an appointment.")
    return redirect("customer-home")

def updateAddress(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            user = request.user
            city = request.POST['city']
            address = request.POST.get("address")
            flat_name = request.POST.get("flat_name")
            landmark = request.POST.get("landmark")
            pincode = request.POST.get("pincode")
            user.city = city
            user.address = address
            user.flat_name = flat_name
            user.landmark = landmark
            user.pincode = pincode
            user.save()

            messages.success(
                request, "You have successfully updated your address.")
            return redirect(f'../cart')
        messages.error(request, "Fill the address form correctly.")
        return redirect("customer-home")
    messages.error(request, "You must login to update Address.")
    return redirect("customer-home")

@csrf_exempt
def paymentHandler(request):
    if request.method == "POST":

        cart = request.user.cart
        price = cart.total_price

        order = Order.objects.create(user=request.user, total_price = price)

        # order.save()
        for item in cart.orderServices.all():
            order.orderServices.add(item)

        order.save()
        cart.orderServices.clear()
        cart.save()

        return render(request, 'customer/payment_succesful.html')
    

    # def success(request):

from django.http import HttpResponse

@csrf_exempt
def handlepayment(request):
    if request.method=='POST':
        x=request.POST
        if x.get('code')=='PAYMENT_SUCCESS':
            dummy_ob=Dummy.objects.get(pk=x.get('transactionId'))
            appointment = Dummy(appointment_user=dummy_ob.appointment_user,Service=dummy_ob.Service, PatientName=dummy_ob.PatientName,
                                      Age=dummy_ob.Age, Sex=dummy_ob.Sex, Status=dummy_ob.Status, phone=dummy_ob.phone, slot_date=dummy_ob.slot_date)
            appointment.save()
            messages.success(
                request, "Your payment is success and request has been received and we'll notify you shortly about the confirmation.")
            return HttpResponseRedirect(reverse('customer-home'))
        messages.failure(
                request, "Your payment is failed please try again ")
        return HttpResponseRedirect(reverse('customer-home'))
    

@csrf_exempt
def handlerecharge(request):
    if request.method=='POST':
        x=request.POST
        print(x)
        if x.get('code')=='PAYMENT_SUCCESS':
            recharge_obj=Recharge.objects.get(pk=x.get('transactionId'))
            api_url = 'https://www.watduwant.com/api/recharge'
            csrf_token = get_csrf_token()

            request_data = {
                'mobile_or_dth':recharge_obj.number,
                'amount':recharge_obj.amount,
                'operator':recharge_obj.operator,
                'recharge_type':recharge_obj.rechargeType
            }

            try:
                headers = {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token
                }
                response = requests.post(api_url, json=request_data, headers=headers)

                if not response.ok:
                    messages.failure(request, "Your recharge is failed kindly use these transaction details to get refund your transaction deatils are :")
                    return HttpResponseRedirect(reverse('customer-home'))
                response_data = response.json()
                if response.ok:
                    if response_data['status'] == 1:
                        messages.success(request, "Your Recharge is success")
                        return HttpResponseRedirect(reverse('customer-home'))
                    elif response_data['status'] == 3:
                        messages.failure(request, "Your recharge is failed kindly use these transaction details to get refund your transaction deatils are :")
                        return HttpResponseRedirect(reverse('customer-home'))

            except Exception as error:
                print(f'API request error: {error}')
            messages.success(
                request, "Your payment is success and request has been received and we'll notify you shortly about the confirmation.")
            return HttpResponseRedirect(reverse('customer-home'))
        messages.failure(
                request, "Your payment is failed please try again ")
        return HttpResponseRedirect(reverse('customer-home'))


@csrf_exempt    
def recharge(request):
    if request.method=='POST':
        number=request.POST.get('number')
        amount=request.POST.get('amount')
        rechargeType=request.POST.get('rechargeType')
        operator=request.POST.get('operator')
        now=datetime.datetime.now()
        current_time=now.strftime("%H:%M:%S")
        recharge=Recharge(number=number,amount=amount,rechargeType=rechargeType,operator=operator,created_at=current_time)
        recharge.save()
        recharge_obj=Recharge.objects.get(number=number,amount=amount,rechargeType=rechargeType,operator=operator,created_at=current_time)
        x=PhonePe(merchant_id="PGTESTPAYUAT",phone_pe_salt='099eb0cd-02cf-4e2a-8aca-3e6c6aff0399',phone_pe_host='https://api-preprod.phonepe.com/apis/pg-sandbox',redirect_url='https://www.watduwant.com/rechargehandle/',webhook_url='https://www.watduwant.com/rechargehandle/',
                      redirect_mode= "POST")
        y=x.create_txn(order_id=str(recharge_obj.id),user=str(recharge_obj.id),amount=recharge_obj.amount * 100)
        print(y)
        return redirect(y['data']['instrumentResponse']['redirectInfo']['url'])
    return render(request,'customer/recharge.html')



def get_csrf_token():
    return None
