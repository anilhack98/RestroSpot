from django.db import models
from django.utils.text import slugify  # To automatically generate URL-friendly slugs
from accounts.models import User, UserProfile  # Import custom User and UserProfile models

# Vendor model: represents a vendor in the marketplace
class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    # Override save method to automatically create slug from vendor_name if not provided
    def save(self, *args, **kwargs):
        if not self.vendor_slug:
            self.vendor_slug = slugify(self.vendor_name)  # Converts name to URL-friendly slug
        super().save(*args, **kwargs)  # Call the original save method

    # String representation of the object
    def __str__(self):
        return self.vendor_name
