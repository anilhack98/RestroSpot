from django.contrib import admin   # Import Django's admin module
from .models import Cart,Tax  # Import the Cart model from the current app

# Create a custom admin class for the Cart model
class CartAdmin(admin.ModelAdmin):
    list_display=('user','fooditem','quantity','updated_at') # Specify which fields to display in the admin list view for Cart objects

class TaxAdmin(admin.ModelAdmin):
    list_display=('tax_type','tax_percentage','is_active')


# Register the Cart model with the admin site using the custom CartAdmin configuration
admin.site.register(Cart,CartAdmin)
admin.site.register(Tax,TaxAdmin)
 