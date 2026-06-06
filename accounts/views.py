from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from orders.models import Order
from products.models import Product
from .forms import CustomerRegistrationForm, FarmerRegistrationForm
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from .token import token_generator
from .models import User
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

            user = form.save()

            uid = urlsafe_base64_encode(force_bytes(user.pk))

            token = token_generator.make_token(user)

            verification_link = (
                f"http://{get_current_site(request)}"
                + reverse(
                    'verify_email',
                    kwargs={
                        'uidb64': uid,
                        'token': token
                    }
                )
            )

            send_mail(
                'Verify your email',
                f'Click the link below to verify your email:\n\n{verification_link}',
                'yourgmail@gmail.com',
                [user.email],
                fail_silently=False,
            )

            messages.success(
                request,
                "Account created successfully! Please check your email to verify your account."
            )

            return redirect('user_login')

    else:
        form = CustomerRegistrationForm()

    return render(
        request,
        'accounts/customer_register.html',
        {'form': form}
    )

def verify_email(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except:
        user = None

    if user and token_generator.check_token(user, token):

        user.is_email_verified = True
        user.save()

        messages.success(
            request,
            "Email verified successfully. You can now login."
        )

        return redirect('user_login')

    messages.error(request, "Invalid verification link.")

    return redirect('user_login')

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
            if not user.is_email_verified:
                messages.error(
                    request,
                    "Please verify your email before logging in."
                )
                return redirect('user_login')
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")

            # Admin
            if user.is_superuser:
                return redirect('/admin/')

            # Farmer
            try:

                farmer = FarmerProfile.objects.get(user=user)

                return redirect('farmer_dashboard')

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
    return render(request, 'products/product_list.html', {
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