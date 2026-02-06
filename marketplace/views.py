from django.shortcuts import get_object_or_404,render,redirect  # For rendering templates and fetching objects or returning 404
from menu.models import Category  # Import food categories and items
from vendor.models import Vendor,OpeningHour  # Import Vendor model
from django.db.models import Prefetch  # For optimizing queries with prefetch_related
from menu.models import Category, FoodItem  # Import food categories and items
from django.http import HttpResponse, JsonResponse  # For returning HTTP and JSON responses
from .models import Cart     # Import Cart model
from .context_processors import get_cart_counter,get_cart_amounts    # Import function to get total cart items
from django.contrib.auth.decorators import login_required   # For login-required views
from django.db.models import Q
from accounts.views import check_role_customer  # Import customer role check

from datetime import date,datetime
from orders.forms import OrderForm
from accounts.models import UserProfile

# Marketplace page: list all approved vendor
def marketplace(request):
    # Get all approved vendors whose user accounts are active
    vendors=Vendor.objects.filter(is_approved=True,user__is_active=True)
    # vendors=Vendor.objects.filter(user__is_active=True)
    vendor_count=vendors.count()   # Count total vendors

    context={
        'vendors':vendors,  # Pass vendor list to template
        'vendor_count':vendor_count,  # Pass vendor count to template
    }
    return render(request,'marketplace/listings.html',context)

# Vendor detail page: show vendor and their available food item
def vendor_detail(request,vendor_slug):
    # Get vendor by slug or return 404 if not found
    vendor=get_object_or_404(Vendor,vendor_slug=vendor_slug)

    # Get categories for this vendor and prefetch their available food items
    categories=Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    opening_hours=OpeningHour.objects.filter(vendor=vendor).order_by('day','-from_hour')

    # Check current day's opening Hour
    today_date=date.today()
    today=today_date.isoweekday()

    current_opening_hours=OpeningHour.objects.filter(vendor=vendor,day=today)


    # Get cart items for logged-in user
    if request.user.is_authenticated:
        cart_items=Cart.objects.filter(user=request.user)
    else:
        cart_items=None
    context={
        'vendor':vendor,
        'categories':categories,
        'cart_items':cart_items,
        'opening_hours':opening_hours,
        'current_opening_hours':current_opening_hours,
    }
    return render(request,'marketplace/vendor_detail.html',context)

# Add food item to cart via AJAX
def add_to_cart(request,food_id):
    if request.user.is_authenticated and check_role_customer(request.user):  # User must be logged in AND be a customer
        if request.headers.get('x-requested-with') == 'XMLHttpRequest': # Check AJAX request
            # Check if the food item exists
            try:
                fooditem=FoodItem.objects.get(id=food_id)   # Get the food item
                # Check if the user has already added that food to the cart
                try:
                    chkCart=Cart.objects.get(user=request.user,fooditem=fooditem)
                    # Increase the cart quantity
                    chkCart.quantity += 1 # Increase quantity
                    chkCart.save()
                    return JsonResponse({'status':'success','message':'Increased cart Quantity','cart_counter':get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    # If item not in cart, create new cart entry
                    chkCart=Cart.objects.create(user=request.user,fooditem=fooditem,quantity=1)
                    return JsonResponse({'status':'success','message':'Added the food to cart','cart_counter':get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amounts(request)})
            except Exception as e:
                print(e)
                return JsonResponse({'status':'Failed','message':'This food does not exist!'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid request'})
    else:
        if not request.user.is_authenticated:
            return JsonResponse({'status':'login_required','message':'Please login to continue'})
        else:
            return JsonResponse({'status':'access_denied','message':'Only customers can add items to cart'})

# Decrease quantity of cart item via AJAX
def decrease_cart(request,food_id):
    if request.user.is_authenticated and check_role_customer(request.user):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                fooditem=FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart=Cart.objects.get(user=request.user,fooditem=fooditem)
                    if chkCart.quantity >1:
                        # Decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()  # Remove from cart if quantity becomes 0
                        chkCart.quantity=0
                    return JsonResponse({'status':'success','cart_counter':get_cart_counter(request),'qty':chkCart.quantity,'cart_amount':get_cart_amounts(request)})
                except:
                    return JsonResponse({'status':'Failed','message':'You do not have this item in your cart','qty':chkCart.quantity})
            except:
                return JsonResponse({'status':'Failed','message':'This food does not exist!'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid request'})
    else:
        if not request.user.is_authenticated:
            return JsonResponse({'status':'login_required','message':'Please login to continue'})
        else:
            return JsonResponse({'status':'access_denied','message':'Only customers can modify cart items'})

# 5️⃣ Display the cart page for logged-in users
@login_required(login_url='login')
def cart(request):
    try:
        # Check if user is a customer
        if not check_role_customer(request.user):
            return redirect('vendorDashboard')  # Redirect vendors to their dashboard
    except:
        return redirect('vendorDashboard')  # Handle PermissionDenied exception
    
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')  # Get all cart items for user
    context={
        'cart_items':cart_items,
    }
    return render(request,'marketplace/cart.html',context)

# 6️⃣ Delete a cart item via AJAX
def delete_cart(request,cart_id):
    if request.user.is_authenticated and check_role_customer(request.user):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Check if the cart item exist
                cart_item=Cart.objects.get(user=request.user,id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status':'success','message':'cart item has been deleted!','cart_counter':get_cart_counter(request),'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Failed','message':'Cart Item does not exist!'})
        else:
            return JsonResponse({'status':'Failed','message':'Invalid request!'})
    else:
        if not request.user.is_authenticated:
            return JsonResponse({'status':'login_required','message':'Please login to continue'})
        else:
            return JsonResponse({'status':'access_denied','message':'Only customers can delete cart items'})

def search(request):
    # Get search parameters safely with defaults
    keyword = request.GET.get('keyword', '')
    address = request.GET.get('address', '')
    latitude = request.GET.get('lat', '')
    longitude = request.GET.get('lng', '')
    
    print(f'Searching for: keyword="{keyword}", address="{address}", lat="{latitude}", lng="{longitude}"')
    
    # Filter vendors by restaurant name if keyword provided
    if keyword:
        # Get vendors that have food items matching the keyword
        vendors_with_matching_food = FoodItem.objects.filter(
            food_title__icontains=keyword,
            is_available=True
        ).values_list('vendor', flat=True)
        
        # Q is used to build complex database queries
        # Search vendors by name OR vendors that have matching food items
        vendors = Vendor.objects.filter(
            Q(id__in=vendors_with_matching_food) | 
            Q(vendor_name__icontains=keyword),
            is_approved=True,
            user__is_active=True
        ).distinct()
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context) 

@login_required(login_url='login')
def checkout(request):
    try:
        # Check if user is a customer
        if not check_role_customer(request.user):
            return redirect('vendorDashboard')  # Redirect vendors to their dashboard
    except:
        return redirect('vendorDashboard')  # Handle PermissionDenied exception
    
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    if cart_count <=0:
        return redirect('marketplace')
    
    user_profile=UserProfile.objects.get(user=request.user)
    default_values={
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'phone':request.user.phone_number,
        'email':request.user.email,
        'address':user_profile.address,
        'country':user_profile.country,
        'state':user_profile.state,
        'city':user_profile.city,
        'pin_code':user_profile.pin_code,
    }
    form=OrderForm(initial=default_values)
    context={
        'form':form,
        'cart_items':cart_items,
    }
    return render(request,'marketplace/checkout.html',context)