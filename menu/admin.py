from django.contrib import admin  # Import Django admin module
from .models import Category,FoodItem   # Import Category and FoodItem models

# Customize admin for Category model
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('category_name',)}  # Automatically fill the 'slug' field based on 'category_name'
    list_display=('category_name','vendor','updated_at')  # Columns to display in the admin list view
    search_fields=('category_name','vendor__vendor_name')  # Fields that can be searched in the admin search box

# Customize admin for FoodItem model
class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('food_title',)}  # Automatically fill the 'slug' field based on 'food_title'
    list_display=('food_title','category','vendor','price','is_available','updated_at') # Columns to display in the admin list view
    search_fields=('food_title','category__category_name','vendor__vendor_name','price')  # Fields that can be searched in the admin search box
    list_filter=('is_available',) # Add filter options in the admin sidebar for 'is_available'

# Register the models with the admin site using the custom admin classes
admin.site.register(Category,CategoryAdmin)
admin.site.register(FoodItem,FoodItemAdmin)

