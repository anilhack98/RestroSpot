from django.shortcuts import render, redirect
from django.http import HttpResponse
from orders.models import Order
from vendor.forms import VendorForm
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages,auth
from .utils import detectUser
from django.contrib.auth.decorators import login_required,user_passes_test
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

from django.core.exceptions import PermissionDenied

from vendor.models import Vendor

from django .template.defaultfilters import slugify


# Restrict Vendor from accessing the customer page
def check_role_vendor(user):
    if user.role==1:   # Vendor role
        return True
    else:
        raise PermissionDenied
    
# Restrict customer from accessing the vendor page
def check_role_customer(user):
    if user.role==2:  # Customer role
        return True
    else:
        raise PermissionDenied

def registerUser(request):
    # Prevent logged-in users from registering again
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in.')
        return redirect('myAccount')
    elif request.method == 'POST':
        form = UserForm(request.POST)

        # Validate form input
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create a new user
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password
            )
            # Activate user and assign customer role
            user.is_active = True
            user.role = User.CUSTOMER
            user.save()

            # Update user profile address
            profile = UserProfile.objects.get(user=user)
            profile.address = form.cleaned_data['address']
            profile.save()

            # Send Email Verification
            #send_verification_email(request,user)
            
            messages.success(request, 'Your account has been registered successfully!')
            return redirect('registerUser')
    else:
        form = UserForm()

    context = {'form': form}
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    # Prevent logged-in users from registering again
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in.')
        return redirect('myAccount')

    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        # Validate both user and vendor forms
        if form.is_valid() and v_form.is_valid():
            # Create vendor user
            user = User.objects.create_user(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            user.role = User.VENDOR
            user.save()

            # Create vendor profile
            vendor = v_form.save(commit=False)
            vendor.user = user
            # Generate unique vendor slug
            vendor_name=v_form.cleaned_data['vendor_name']
            vendor.vendor_slug=slugify(vendor_name)+'-'+str(user.id)

            # ✅ SAFELY get or create profile
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            vendor.user_profile = user_profile

            vendor.save()

            messages.success(
                request,
                'Your account has been registered successfully! Please wait for approval.'
            )
            return redirect('login')
         # Print form errors for debugging
        else:
            print('Invalid Form')
            print('UserForm Errors:', form.errors)
            print('VendorForm Errors:', v_form.errors)

    else:
        form = UserForm()
        v_form = VendorForm()

    return render(request, 'accounts/registerVendor.html', {
        'form': form,
        'v_form': v_form,
    })


# def activate(request,uidb64,token):
#     # Activate the user by setting the is_activate status to True
#     try:
#         uid=urlsafe_base64_decode(uidb64).decode()
#         user=user.default_manager.get(pk=uid)
#     except(TypeError,ValueError,OverflowError,User.DoesNotExist):
#         user=None
#     if user is not None and default_token_generator.check_token(user,token):
#         user.is_active=True
#         user.save()
#         messages.success(request,'Congratulation You account is activated.')
#         return redirect('myAccount')
#     else:
#         messages.error(request,'Invalid activation link')
#         return redirect('myAccount')
    
def login(request):
    if request.user.is_authenticated:
        messages.warning(request,'You are already logged in.')
        return redirect('myAccount')
    elif request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']

        # Authenticate user
        user=auth.authenticate(email=email,password=password)

        if user is not None:
            auth.login(request,user)
            messages.success(request,'You are now logged in.')
            return redirect('myAccount')
        else:
            messages.error(request,'Invalid login credentials.')
            return redirect('login')
    return render(request,'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request,'You are logged out.')
    return redirect('login')


@login_required(login_url='login')
def myAccount(request):
    User=request.user
    redirectUrl=detectUser(User)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customerDashboard(request):
    orders=Order.objects.filter(user=request.user,is_ordered=True)
    recent_orders=orders[:5]  # Shows the recent 5 orders
    context = {
        'customer': request.user,  # Pass the logged-in user as 'customer'
        'orders':orders,
        'orders_count':orders.count(),
        'recent_orders':recent_orders,
    }
    return render(request, 'accounts/customerDashboard.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request,'accounts/vendorDashboard.html')

# def forgot_password(request):
#     if request.method=='POST':
#         email=request.POST['email']

#         if User.objects.filter(email=email).exists():
#             user=User.objects.get(email__exact=email)

#             # send Reset password email
#             # send_password_reset_email(request,user)

#             messages.success(request,'Password reset link has been sent to your email address')
#             return redirect('login')
#         else:
#             messages.error(request,'Account does not exist')
#             return render(request,'accounts/forgot_password')
#     return render(request,'accounts/forgot_password.html')

# def reset_password_validate(request):
#     return render(request,'accounts/forgot_password.html')

# def reset_password(request):
#     if request.method == 'POST':
#         password = request.POST['password']
#         confirm_password = request.POST['confirm_password']

#         if password == confirm_password:
#             uid = request.session.get('uid')
#             user = User.objects.get(pk=uid)
#             user.set_password(password)
#             user.is_active = True
#             user.save()

#             messages.success(request, 'Your password has been reset successfully!')
#             return redirect('login')

#         else:
#             messages.error(request, 'Passwords do not match')
#             return redirect('reset_password')
    
#     return render(request, 'accounts/reset_password.html')