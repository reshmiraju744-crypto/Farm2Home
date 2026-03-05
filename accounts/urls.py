from accounts import views
from django.urls import path
urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.register_choice, name='register_choice'),
    path('customer_register/', views.customer_register, name='customer_register'),
    path('farmer_register/', views.farmer_register, name='farmer_register'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('edit-profile/', views.edit_user, name='edit_user'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

]
