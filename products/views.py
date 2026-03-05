from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from wishlist.models import Wishlist
from .models import Product
from .forms import ProductForm
from farmers.models import FarmerProfile
from django.shortcuts import get_object_or_404


from django.db.models import Q
from .models import Product, Category

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    query = request.GET.get('q')
    category_id = request.GET.get('category')

    # 🔍 Search filter
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # 📂 Category filter
    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
    })



@login_required
def add_product(request):
    try:
        farmer_profile = FarmerProfile.objects.get(user=request.user)
    except FarmerProfile.DoesNotExist:
        return redirect('product_list')

    if farmer_profile.approval_status != "Approved":
        return redirect('product_list')

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = farmer_profile
            product.save()

            action = request.POST.get("action")

            if action == "save_add":
                return redirect('add_product')   # reload same page
            else:
                return redirect('my_products')  # go to product list
    else:
        form = ProductForm()

    return render(request, 'products/add_products.html', {'form': form})

@login_required
def my_products(request):
    try:
        farmer_profile=FarmerProfile.objects.get(user=request.user)
    except FarmerProfile.DoesNotExist:
        return redirect('product_list')
    products=Product.objects.filter(farmer=farmer_profile)
    return render(request,'products/my_products.html',{'products':products})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Security check: only owner can edit
    if product.farmer.user != request.user:
        return redirect('my_products')

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('my_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_products.html', {'form': form})


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Security check
    if product.farmer.user != request.user:
        return redirect('my_products')

    if request.method == "POST":
        product.delete()
        return redirect('my_products')

    return render(request, 'products/delete_products.html', {'product': product})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_details.html', {'product': product})


from .models import Product, Category

def category_products(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)

    return render(request, "products/category_products.html", {
        "category": category,
        "products": products
    })