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


# def send_verification_email(request, user):
#     from_email = settings.DEFAULT_FROM_EMAIL
#     current_site = get_current_site(request)
#     mail_subject = 'Please activate your account.'
#     message = render_to_string('accounts/emails/account_verification_email.html', {
#         'user': user,
#         'domain': current_site,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': default_token_generator.make_token(user),
#     })
#     to_email = user.email
#     mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
#     mail.send()


# def send_password_reset_email(request, user):
#     from_email = settings.DEFAULT_FROM_EMAIL
#     current_site = get_current_site(request)
#     mail_subject = 'Reset your password.'
#     message = render_to_string('accounts/emails/reset_password_email.html', {
#         'user': user,
#         'domain': current_site,
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': default_token_generator.make_token(user),
#     })
#     to_email = user.email
#     mail = EmailMessage(mail_subject, message, from_email, to=[to_email])
#     mail.send()
