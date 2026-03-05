from django.db import models
from accounts.models import User

FARMER_TYPES = (
    ('Individual', 'Individual'),
    ('SHG', 'Self Help Group'),
    ('Cooperative', 'Cooperative'),
)

APPROVAL_STATUS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
)

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    farm_name = models.CharField(max_length=100)
    farmer_type = models.CharField(max_length=20, choices=FARMER_TYPES)
    years_experience = models.PositiveIntegerField()
    farm_address = models.TextField()
    village = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    id_proof_type = models.CharField(max_length=50)
    id_proof_number = models.CharField(max_length=50)
    certificate = models.FileField(upload_to='farmer_certificates/', blank=True, null=True)
    approval_status = models.CharField(max_length=10, choices=APPROVAL_STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.farm_name} ({self.approval_status})"

