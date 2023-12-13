import imp
from .views import home, account, showCart
from django.urls import path
from customer import views
urlpatterns = [
    path('', home, name='customer-home'),
    path('terms',views.terms,name='terms'),
    path('account', account, name='account'),
    path('show_details/<shop_id>', views.show_details, name='show_details'),
    path('bookService', views.BookPathologicalService, name='book_service'),
    path('loadServiceTime/', views.serviceTime, name="loadtimes"),
    path('cart/', views.showCart, name="cart"),
    path('updateAddress/', views.updateAddress, name="updateAddress"),
    path('paymentHandler/', views.paymentHandler, name="paymentHandler"),
    path('paymenthandle/',views.handlepayment,name='paymenthandle'),
    path('recharge',views.recharge,name='recharge'),
    path('rechargehandle/',views.handlerecharge,name='rechargehandle'),
    path('about',views.about,name='about')
    # path('list', views.all_list, name='clinic_list'),
]
