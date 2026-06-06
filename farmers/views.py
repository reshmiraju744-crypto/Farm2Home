from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from notifications.models import Notification
from .models import FarmerProfile
from products.models import Product
from orders.models import OrderItem
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import json

@login_required
def farmer_dashboard(request):

    try:
        farmer = FarmerProfile.objects.get(user=request.user)

    except FarmerProfile.DoesNotExist:
        return redirect('product_list')

    # Farmer products
    products = Product.objects.filter(farmer=farmer)

    # Order items
    order_items = OrderItem.objects.filter(
        product__farmer=farmer
    ).select_related('order')

    # Stats
    total_products = products.count()

    total_orders = order_items.count()

    pending_orders = order_items.filter(
        order__status='Pending'
    ).count()

    from django.db.models import F, Sum

    total_earnings = order_items.filter(
        order__status='Delivered'
    ).aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    monthly_data = (
        order_items.filter(
            order__status='Delivered'
        )
        .annotate(month=TruncMonth('order__created_at'))
        .values('month')
        .annotate(total=Sum('price'))
        .order_by('month')
    )

    months = []
    earnings = []

    for item in monthly_data:
        if item['month']:
            months.append(item['month'].strftime('%b'))
            earnings.append(float(item['total']))

    context = {

        'farmer': farmer,

        'total_products': total_products,

        'total_orders': total_orders,

        'pending_orders': pending_orders,

        'total_earnings': total_earnings,

        'months': json.dumps(months),

        'earnings': json.dumps(earnings),

        'recent_orders': order_items.order_by(
            '-order__created_at'
        ),

        'notifications': notifications,

        'unread_count': unread_count,
    }

    return render(
        request,
        'farmers/farmer_dashboard.html',
        context
    )



@login_required
def edit_farmer_profile(request):
    farmer = request.user.farmerprofile

    if request.method == "POST":
        farm_name = request.POST.get('farm_name')
        farm_address = request.POST.get('farm_address')
        village = request.POST.get('village')
        district = request.POST.get('district')

        # Validation (Prevents NOT NULL errors)
        if not farm_name or not farm_address or not village or not district:
            messages.error(request, "All fields are required!")
            return redirect('edit_farmer_profile')

        farmer.farm_name = farm_name
        farmer.farm_address = farm_address
        farmer.village = village
        farmer.district = district

        farmer.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('farmer_dashboard')

    return render(request, 'farmers/edit_profile.html', {'farmer': farmer})

@login_required
def view_farmer_profile(request):
    farmer = request.user.farmerprofile
    return render(request, 'farmers/view_profile.html', {'farmer': farmer})

@login_required
def delete_farmer_profile(request):
    farmer = request.user.farmerprofile

    if request.method == "POST":
        user = request.user
        farmer.delete()     # delete profile
        user.delete()       # delete user account also
        return redirect('home')  # or login page

    return render(request, 'farmers/delete_profile.html')

