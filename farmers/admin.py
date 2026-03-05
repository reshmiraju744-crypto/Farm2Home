from django.contrib import admin
from .models import FarmerProfile


@admin.action(description="Approve selected farmers")
def approve_farmers(modeladmin, request, queryset):
    queryset.update(approval_status='Approved')


@admin.action(description="Reject selected farmers")
def reject_farmers(modeladmin, request, queryset):
    queryset.update(approval_status='Rejected')


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm_name', 'approval_status')
    list_filter = ('approval_status',)
    actions = [approve_farmers, reject_farmers]
