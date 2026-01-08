from django.urls import path  # Import path function to define URL patterns
from .import views # Import views from the current app


# Define URL patterns for the marketplace app
urlpatterns=[
    # URL for the main marketplace page
    path('',views.marketplace,name='marketplace'),

    # URL for a specific vendor's detail page
    # Example: /vendor-slug/ will show details of that vendor
     path('<slug:vendor_slug>/', views.vendor_detail, name='vendor_detail'),


     # URL to add a food item to the cart
    # Example: /add_to_cart/5/ adds the food item with ID 5
     path('add_to_cart/<int:food_id>/',views.add_to_cart,name='add_to_cart'),

     # URL to decrease the quantity of a food item in the cart
    # Example: /decrease_cart/5/ decreases quantity of food item with ID 5 
      path('decrease_cart/<int:food_id>/', views.decrease_cart, name='decrease_cart'),

      # URL to delete a specific cart item
    # Example: /delete_cart/10/ deletes the cart item with ID 10
      path('delete_cart/<int:cart_id>/',views.delete_cart,name='delete_cart'),

]