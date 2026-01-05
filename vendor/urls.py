from django.urls import path,include  # Import path function to define URLs
from . import views   # Import views from the current vendor app
from accounts import views as AccountViews   # Import views from accounts app

# Define URL patterns for vendor-related pages
urlpatterns=[
    # Vendor dashboard (homepage for vendor) → uses account app's view
    path('',AccountViews.vendorDashboard,name='vendor'),

    # Vendor profile page
    path('profile/', views.vendorprofile,name='vendorprofile'),

    # Menu builder main page (list of categories and food items)
    path('menu-builder/',views.menu_builder,name='menu_builder'),

    # Show food items under a specific category
    path('menu-builder/category/<int:pk>/',views.fooditems_by_category,name='fooditems_by_category'),

    # Category CRUD URLs
    path('menu-builder/category/add/',views.add_category,name='add_category'),
    path('menu-builder/category/edit/<int:pk>/',views.edit_category,name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/',views.delete_category,name='delete_category'),

    # Food Item CRUD URLs
    path('menu-builder/food/add/',views.add_food,name='add_food'),
    path('menu-builder/food/edit/<int:pk>/',views.edit_food,name='edit_food'),
     path('menu-builder/food/delete/<int:pk>/',views.delete_food,name='delete_food'),
]