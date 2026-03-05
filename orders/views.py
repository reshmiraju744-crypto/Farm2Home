from django.contrib import messages
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from .models import Order,OrderItem
from cart.models import CartItem
from products.models import Product
from farmers.models import FarmerProfile
from .forms import CheckoutForm

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('view_cart')

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            total = 0

            for item in cart_items:
                if item.product.stock < item.quantity:
                    return redirect('view_cart')
                total += item.product.price * item.quantity

            # Save data temporarily in session
            request.session['checkout_data'] = form.cleaned_data
            request.session['cart_total'] = float(total)

            return redirect('payment_page')

    else:
        form = CheckoutForm()

    return render(request, 'orders/checkout.html', {'form': form})

#orders success
@login_required
def order_success(request):
    return render(request,'orders/order_success.html')

#orders history page
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})


#farmer orders
from django.db.models import Sum, F
from orders.models import OrderItem

@login_required
def farmer_orders(request):
    farmer = FarmerProfile.objects.filter(user=request.user).first()

    if not farmer:
        return redirect('home')

    # Get order items for this farmer
    order_items = OrderItem.objects.filter(
        product__farmer__user=request.user
    ).select_related('order', 'product')

    # 📊 Stats
    total_products = Product.objects.filter(farmer=farmer).count()

    total_orders = order_items.values('order').distinct().count()

    pending_orders = order_items.filter(
        order__status='Pending'
    ).values('order').distinct().count()

    total_earnings = order_items.filter(
        order__status='Delivered'
    ).aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0

    recent_orders = order_items.order_by('-order__created_at')[:5]

    print("Farmer:", request.user)
    print("Order items count:", order_items.count())

    return render(request, 'farmers/farmer_dashboard.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_earnings': total_earnings,
        'recent_orders': recent_orders,
    })


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

    # 🔥 Double check stock
    for item in cart_items:
        if item.product.stock < item.quantity:
            return redirect('view_cart')

    # Create Order
    order = Order.objects.create(
        user=request.user,
        total_price=total,
        **checkout_data
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

        product = item.product
        product.stock -= item.quantity
        product.save()

    cart_items.delete()

    request.session.pop('checkout_data', None)
    request.session.pop('cart_total', None)
    return redirect('order_success')
