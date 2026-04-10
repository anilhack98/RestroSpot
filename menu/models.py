from django.db import models
from vendor.models import Vendor  # Import Vendor model

# 1️⃣ Category model: represents a category of food under a vendor
class Category(models.Model):
    """
    A grouping category for food items (e.g., 'Beverages', 'Main Course', 'Desserts').
    Categories are strictly scoped to a single Vendor.
    """
    vendor=models.ForeignKey(Vendor,on_delete=models.CASCADE) # Each category belongs to a vendor; deleting vendor deletes categories
    category_name=models.CharField(max_length=50)  # Name of category, must be unique
    slug=models.SlugField(max_length=100,unique=True) # URL-friendly version of the category name
    description=models.TextField(max_length=250,blank=True)  # Optional description
    created_at=models.DateTimeField(auto_now_add=True)  # Timestamp when created
    updated_at=models.DateTimeField(auto_now=True)  # Timestamp when last updated

    class Meta:
        verbose_name='category'
        verbose_name_plural='categories'
    
    # Automatically capitalize the category name before saving
    def clean(self):
        self.category_name=self.category_name.capitalize()

    # String representation of the object
    def __str__(self):
        return self.category_name
    
from django.core.validators import MinValueValidator

# 2️⃣ FoodItem model: represents a food item under a category and vendor
class FoodItem(models.Model):
    """
    An individual purchasable product offered by a Vendor.
    Requires relationship to both a Vendor and a specific Category.
    """
    vendor=models.ForeignKey(Vendor,on_delete=models.CASCADE)  # Each food item belongs to a vendor
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='fooditems')
    food_title=models.CharField(max_length=50)
    slug=models.SlugField(max_length=100,unique=True)
    description=models.TextField(max_length=250,blank=True)
    price=models.DecimalField(max_digits=10,decimal_places=2, validators=[MinValueValidator(0.01)])
    image=models.ImageField(upload_to='foodimages')
    is_available=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def clean(self):
        # Validate that price is not zero or negative
        if self.price is not None and self.price <= 0:
            from django.core.exceptions import ValidationError
            raise ValidationError({'price': 'Price must be greater than zero.'})
    
    def __str__(self):
        return self.food_title
