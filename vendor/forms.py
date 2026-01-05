from django import forms  # Import Django forms module
from .models import Vendor  # Import Vendor model
from accounts.validators import allow_only_images_validator   # Custom validator to allow only image files

# Form to create or update a Vendor
class VendorForm(forms.ModelForm):
    # Customize the vendor_license field
    vendor_license=forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info'}),validators=[allow_only_images_validator])
    class Meta:
        model=Vendor
        fields=['vendor_name','vendor_license']