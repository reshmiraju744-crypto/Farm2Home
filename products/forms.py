from django import forms
from .models import Product
from .models import Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['category'].empty_label = "Select Category"



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review']