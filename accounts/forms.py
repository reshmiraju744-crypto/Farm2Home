from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from farmers.models import FarmerProfile, FARMER_TYPES

# ---------------------------
# CUSTOMER REGISTRATION FORM
# ---------------------------
class CustomerRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)
    # Address fields (can be saved later in profile or extended model)
    house_name = forms.CharField(max_length=100, required=True)
    place = forms.CharField(max_length=50, required=True)
    district = forms.CharField(max_length=50, required=True)
    state = forms.CharField(max_length=50, required=True)
    pincode = forms.CharField(max_length=10, required=True)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'customer'
        if commit:
            user.save()
        return user

# ---------------------------
# FARMER REGISTRATION FORM
# ---------------------------
class FarmerRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)

    farm_name = forms.CharField(max_length=100, required=True)
    farmer_type = forms.ChoiceField(choices=FARMER_TYPES, required=True)
    years_experience = forms.IntegerField(min_value=0, required=True)
    farm_address = forms.CharField(widget=forms.Textarea, required=True)
    village = forms.CharField(max_length=50, required=True)
    district = forms.CharField(max_length=50, required=True)
    id_proof_type = forms.CharField(max_length=50, required=True)
    id_proof_number = forms.CharField(max_length=50, required=True)
    certificate = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'farmer'
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            FarmerProfile.objects.create(
                user=user,
                farm_name=self.cleaned_data['farm_name'],
                farmer_type=self.cleaned_data['farmer_type'],
                years_experience=self.cleaned_data['years_experience'],
                farm_address=self.cleaned_data['farm_address'],
                village=self.cleaned_data['village'],
                district=self.cleaned_data['district'],
                id_proof_type=self.cleaned_data['id_proof_type'],
                id_proof_number=self.cleaned_data['id_proof_number'],
                certificate=self.cleaned_data.get('certificate'),
            )

        return user
