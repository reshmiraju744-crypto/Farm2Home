from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import CartItem
from products.models import Product


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.stock <= 0:
        return redirect('product_list')

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        if product.stock > cart_item.quantity:
            cart_item.quantity += 1
            cart_item.save()

    return redirect('view_cart')

@login_required
def view_cart(request):
    items = CartItem.objects.filter(user=request.user)

    total = 0
    for item in items:
        item.subtotal = item.product.price * item.quantity
        total += item.subtotal

    return render(request, 'cart/view_cart.html', {
        'items': items,
        'total': total
    })



@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    return redirect('view_cart')


@login_required
def decrease_quantity(request,pk):
    item = get_object_or_404(CartItem,pk=pk , user=request.user)

    if item.quantity>1:
        item.quantity -=1
        item.save()
    else:
        item.delete()

    return redirect('view_cart')