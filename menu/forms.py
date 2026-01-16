from django import forms # Import Django forms module

from accounts.validators import allow_only_images_validator  # Custom validator to allow only image files
from .models import Category,FoodItem  # Import Category and FoodItem models

# 1️⃣ Form for Category model
class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        fields=['category_name','description']

# 2️⃣ Form for FoodItem model
class FoodItemForm(forms.ModelForm):
    image=forms.FileField(widget=forms.FileInput(attrs={'class':'btn btn-info w-100'}),validators=[allow_only_images_validator])
    
    # Creates a decimal number field
    price=forms.DecimalField(
        min_value=0,  #Prevents negative values
        decimal_places=2, # Allows only 2 digits after decimal
        widget=forms.NumberInput(attrs={'class':'form-control', 'step': '0.01', 'min': '0'})
    )
    class Meta:
        model=FoodItem
        fields=['category','food_title','description','price','image','is_available']
