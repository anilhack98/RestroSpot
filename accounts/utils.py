from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings

"""
    This function checks the role of the logged-in user
    and returns the appropriate redirect URL.
    """
def detectUser(user):
    # If the user role is Vendor (role = 1)
    if user.role == 1:
        redirectUrl = 'vendorDashboard'  # redirect to vendor dashboard
        return redirectUrl
    
    # If the user role is Customer (role = 2)
    elif user.role == 2:
        redirectUrl = 'customerDashboard'  # redirect to customer dashboard
        return redirectUrl
    
    # If the user has no role but is a Super Admin
    elif user.role is None and user.is_superAdmin:
        redirectUrl = '/admin'  # redirect to Django admin panel
        return redirectUrl

