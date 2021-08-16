from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('user/', views.userPage, name="user-page"),

    path('account/', views.accountSettings, name="account"),
    path('products/', views.products, name='product'),

    path('orders/', views.orderDetails, name='order-details'),

    path('customer/<str:customer_id>/', views.customer, name='customer'),

    path('create_order/<str:customer_id>/',
         views.create_order, name='create_order'),
    path('update_order/<str:order_id>/',
         views.update_order, name='update_order'),
    path('delete_order/<str:order_id>/',
         views.delete_order, name='delete_order'),
]
