from django import forms
from .models import Order, Address


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'address', 'city', 'pincode']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'label',
            'full_name',
            'phone',
            'address',
            'city',
            'pincode'
        ]