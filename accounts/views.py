from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from orders.models import Order
from products.models import Product
from .forms import CustomerRegistrationForm, FarmerRegistrationForm

# -----------------------
# Home Page
# -----------------------

from products.models import Category, Product
from .models import UserProfile


def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    return render(request, "base.html", {
        "categories": categories,
        "products": products
    })
# -----------------------
# Customer Registration
# -----------------------
def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer account created successfully! Please login.")
            return redirect('user_login')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/customer_register.html', {'form': form})

# -----------------------
# Farmer Registration
# -----------------------
def farmer_register(request):
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user=form.save()
            FarmerProfile.objects.create(user=user,farm_name=form.cleaned_data.get("farm_name",))
            messages.success(request, "Farmer account created successfully! Waiting for admin approval.")
            return redirect('user_login')
    else:

        form = FarmerRegistrationForm()
    return render(request, 'accounts/farmer_register.html', {'form': form})



def register_choice(request):
    return render(request, 'accounts/register_choice.html')
# -----------------------
# Login
# -----------------------
from farmers.models import FarmerProfile

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")

            # Admin
            if user.is_superuser:
                return redirect('/admin/')

            # Farmer
            try:
                farmer = FarmerProfile.objects.get(user=user)

                if farmer.approval_status == 'Approved':
                    return redirect('farmer_orders')

                elif farmer.approval_status == 'Pending':
                    messages.error(request, "Your account is waiting for admin approval.")
                    return redirect('user_login')

                elif farmer.approval_status == 'Rejected':
                    messages.error(request, "Your account has been rejected by admin.")
                    return redirect('user_login')

            except FarmerProfile.DoesNotExist:
                pass

            # Customer
            return redirect('customer_dashboard')

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/user_login.html')

# -----------------------
# Logout
# -----------------------
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')




@login_required
def customer_dashboard(request):
    products = Product.objects.all()
    print(products)
    return render(request, 'accounts/customer_dashboard.html', {
        'products': products
    })

@login_required
def user_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'accounts/user_profile.html', {'profile': profile})


@login_required
def edit_user(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()

        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')

        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES.get('profile_image')

        profile.save()

        return redirect('user_profile')

    return render(request, 'accounts/edit_user.html', {'profile': profile})



def about(request):
    return render(request, 'accounts/about.html')

def contact(request):
    # Only show approved farmers
    farmers = FarmerProfile.objects.filter(approval_status='Approved')
    return render(request, 'accounts/contact.html', {'farmers': farmers})