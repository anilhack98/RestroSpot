from vendor.models import Vendor  # Import Vendor model from vendor app
from accounts.models import User,UserProfile
# Import User model from accounts app
from django.conf import settings


# This function is a CONTEXT PROCESSOR
# It makes vendor data available in all templates
def get_vendor(request):
    try:
        vendor=Vendor.objects.get(user=request.user)
    except:
        vendor=None
    return dict(vendor=vendor)

def get_user_profile(request):
    try:
        user_profile=UserProfile.objects.get(user=request.user)
    except:
        user_profile=None
    return dict(user_profile=user_profile)

def get_google_api(request):
    return {'GOOGLE_API_KEY':settings.GOOGLE_API_KEY} 