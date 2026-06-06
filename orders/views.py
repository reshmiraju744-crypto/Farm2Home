from django.contrib import messages
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Order, OrderItem, Address
from cart.models import CartItem
from products.models import Product, Review
from farmers.models import FarmerProfile
from .forms import CheckoutForm, AddressForm
from notifications.models import Notification
import json
from django.db.models.functions import TruncMonth

@login_required
def checkout(request):
    addresses = Address.objects.filter(user=request.user)

    if not addresses.exists():
        return redirect('save_address')

    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('view_cart')

    if request.method == "POST":

        address_id = request.POST.get('address_id')

        if not address_id:
            return redirect('checkout')

        address = Address.objects.get(
            id=address_id,
            user=request.user
        )

        total = 0

        for item in cart_items:
            if item.product.stock < item.quantity:
                return redirect('view_cart')

            total += item.product.price * item.quantity

        request.session['checkout_data'] = {
            'full_name': address.full_name,
            'phone': address.phone,
            'address': address.address,
            'city': address.city,
            'pincode': address.pincode,
        }

        request.session['cart_total'] = float(total)

        return redirect('payment_page')

    return render(
        request,
        'orders/checkout.html',
        {
            'addresses': addresses
        }
    )
#orders success
@login_required
def order_success(request):
    return render(request,'orders/order_success.html')

# orders history page
@login_required
def order_history(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('orderitem_set__product')

    reviewed_products = Review.objects.filter(
        user=request.user
    ).values_list('product_id', flat=True)

    return render(request, 'orders/order_history.html', {
        'orders': orders,
        'reviewed_products': reviewed_products
    })


#farmer orders
from django.db.models import Sum, F
from orders.models import OrderItem

@login_required
def farmer_orders(request):

    farmer = FarmerProfile.objects.filter(user=request.user).first()
    if not farmer:
        return redirect('home')
    # ================= ORDER ITEMS =================
    order_items = OrderItem.objects.filter(product__farmer__user=request.user).select_related(
        'order',
        'product'
    )

    # ================= STATS =================
    total_products = Product.objects.filter(farmer=farmer).count()
    total_orders = order_items.values('order').distinct().count()
    pending_orders = order_items.filter(order__status='Pending').values(
        'order'
    ).distinct().count()

    total_earnings = order_items.filter(
        order__status='Delivered'
    ).aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0

    # ================= RECENT ORDERS =================
    recent_orders = order_items.order_by('-order__created_at')

    # ================= NOTIFICATIONS =================
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    print("Farmer:", request.user)
    print("Order items count:", order_items.count())
    # ================= MONTHLY EARNINGS =================

    monthly_data = (order_items.filter(
            order__status='Delivered'
        )
        .annotate(
            month=TruncMonth('order__created_at')
        )
        .values('month')
        .annotate(
            total=Sum(
                F('price') * F('quantity')
            )
        )
        .order_by('month')
    )

    months = []
    earnings = []

    for item in monthly_data:
        if item['month']:
            months.append(
                item['month'].strftime('%b')
            )
            earnings.append(
                float(item['total'])
            )
    # ================= RENDER =================
    return render(request, 'farmers/farmer_dashboard.html', {
        'farmer': farmer,
        'notifications': notifications,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_earnings': total_earnings,
        'recent_orders': recent_orders,
        'months': json.dumps(months),
        'earnings': json.dumps(earnings),
    })

@login_required
def farmer_order_detail(request, order_id):

    farmer = request.user.farmerprofile

    order = get_object_or_404(Order, id=order_id)

    items = OrderItem.objects.filter(
        order=order,
        product__farmer=farmer
    )

    return render(
        request,
        'farmers/order_detail.html',
        {
            'order': order,
            'items': items
        }
    )

@login_required
def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id)

    # Check if this farmer owns at least one product in the order
    if not order.orderitem_set.filter(
        product__farmer__user=request.user
    ).exists():
        return redirect('farmer_orders')

    if status in ['Confirmed', 'Delivered']:
        order.status = status
        order.save()

    return redirect('farmer_orders')

#payment
@login_required
def payment_page(request):
    total = request.session.get('cart_total')

    if not total:
        return redirect('view_cart')

    return render(request, 'orders/payment.html', {'total': total})



#confirm payment
@login_required
def confirm_payment(request):

    cart_items = CartItem.objects.filter(user=request.user)

    checkout_data = request.session.get('checkout_data')

    total = request.session.get('cart_total')

    if not checkout_data or not cart_items.exists():

        return redirect('view_cart')

    # ================= STOCK CHECK =================

    for item in cart_items:

        if item.product.stock < item.quantity:

            return redirect('view_cart')

    # ================= CREATE ORDER =================

    order = Order.objects.create(

        user=request.user,

        total_price=total,

        **checkout_data

    )

    # ================= CREATE ORDER ITEMS =================

    for item in cart_items:

        OrderItem.objects.create(

            order=order,

            product=item.product,

            quantity=item.quantity,

            price=item.product.price

        )

        # ================= UPDATE STOCK =================

        product = item.product

        product.stock -= item.quantity

        product.save()

        # ================= SELLER NOTIFICATION =================

        seller = product.farmer.user

        Notification.objects.create(

            user=seller,

            message=f"📦 {request.user.username} ordered {product.name}."

        )

    # ================= CLEAR CART =================

    cart_items.delete()

    request.session.pop('checkout_data', None)

    request.session.pop('cart_total', None)

    return redirect('order_success')


@login_required
def save_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

            return redirect('checkout')

    else:
        form = AddressForm()

    return render(
        request,
        'orders/save_address.html',
        {
            'form': form
        }
    )

@login_required
def edit_address(request, address_id):
    address = Address.objects.get(
        id=address_id,
        user=request.user
    )

    if request.method == 'POST':
        form = AddressForm(
            request.POST,
            instance=address
        )

        if form.is_valid():
            form.save()
            return redirect('checkout')

    else:
        form = AddressForm(instance=address)

    return render(
        request,
        'orders/save_address.html',
        {
            'form': form
        }
    )

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user
    )

    address.delete()

    return redirect('checkout')