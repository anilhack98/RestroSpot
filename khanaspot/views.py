from django.shortcuts import render
from django.http import HttpResponse

from vendor.models import Vendor
from orders.utils import (
    get_recommended_vendors_for_user,
    get_recommended_fooditems_for_user,
)


# Define a view function called 'home' that takes a request object
def home(request):
    # Top vendors (simple popularity: latest approved & active)
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]

    # Personalized recommendations based on order history
    recommended_vendors = get_recommended_vendors_for_user(request.user, limit=8)
    recommended_fooditems = get_recommended_fooditems_for_user(request.user, limit=8)

    # Prepare context data to pass to the template
    context = {
        "vendors": vendors,
        "recommended_vendors": recommended_vendors,
        "recommended_fooditems": recommended_fooditems,
    }
    return render(request, "home.html", context)   # Render the 'home.html' template with the given context