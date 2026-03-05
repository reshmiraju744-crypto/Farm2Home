from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['category'].empty_label = "Select Category"