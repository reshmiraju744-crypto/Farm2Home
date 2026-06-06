from django.urls import path
from . import views

urlpatterns = [
path(
    'mark-notifications-read/',
    views.mark_notifications_read,
    name='mark_notifications_read'
),
]