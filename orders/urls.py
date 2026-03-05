from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.order_success, name='order_success'),
    path('history/', views.order_history, name='order_history'),
    path('farmer-orders/', views.farmer_orders, name='farmer_orders'),
    path('update-status/<int:order_id>/<str:status>/',views.update_order_status, name='update_order_status'),
    path('payment/', views.payment_page, name='payment_page'),
    path('confirm-payment/', views.confirm_payment, name='confirm_payment'),


]
