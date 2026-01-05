from vendor.models import Vendor  # Import Vendor model from vendor app
from accounts.models import User  
# Import User model from accounts app


# This function is a CONTEXT PROCESSOR
# It makes vendor data available in all templates
def get_vendor(request):
    try:
        vendor=Vendor.objects.get(user=request.user)
    except:
        vendor=None
    return dict(vendor=vendor)

