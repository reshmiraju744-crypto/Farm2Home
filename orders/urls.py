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
    path('save-address/',views.save_address,name='save_address'),
    path('address/edit/<int:address_id>/',views.edit_address,name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address,name='delete_address'),
    path('order/<int:order_id>/',views.farmer_order_detail,name='farmer_order_detail'),
]
