from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
path('farmer/edit-profile/', views.edit_farmer_profile, name='edit_farmer_profile'),
path('profile/', views.view_farmer_profile, name='view_farmer_profile'),
path('profile/delete/', views.delete_farmer_profile, name='delete_farmer_profile'),
]
