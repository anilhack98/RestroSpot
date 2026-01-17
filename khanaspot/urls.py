from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from marketplace import views as MarketplaceViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),

    # Include all URLs from accounts app
    # Example: login, register, dashboard, etc.
    path('',include('accounts.urls')),

    # Include all URLs from marketplace app
    # Example: vendors, food items, add to cart
    path('marketplace/',include('marketplace.urls')),

    # Cart page URL
    # This maps directly to the cart view inside marketplace app
      path('cart/',MarketplaceViews.cart,name='cart'),

      # Search Path
      path('search/',MarketplaceViews.search,name='search'),

      # CheckOut
      path('checkout/',MarketplaceViews.checkout,name='checkout'),
      
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
