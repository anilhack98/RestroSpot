from django.db import models  # Import Django's models module

from accounts.models import User  # Import custom User model
from menu.models import FoodItem  # Import FoodItem model

# Define the Cart model
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)  # Link cart item to a user. If user is deleted, their cart items are deleted too.
    fooditem=models.ForeignKey(FoodItem,on_delete=models.CASCADE) # Link cart item to a food item. If the food item is deleted, cart item is deleted.
    quantity=models.PositiveIntegerField()  # Number of this food item in the cart. Cannot be negative.
    created_at=models.DateTimeField(auto_now_add=True)  # Timestamp when the cart item was created
    updated_at=models.DateTimeField(auto_now=True)  # Timestamp when the cart item was last updated

    # Function to represent the object as a string
    def __unicode__(self):
        return self.user  # Returns the user associated with this cart item
 