from django.shortcuts import get_object_or_404, render,redirect  # Import functions to render templates, redirect users, and get objects safely
from django.http import HttpResponse, JsonResponse  # Import JsonResponse for AJAX responses

from menu.forms import CategoryForm,FoodItemForm
from orders.models import Order, OrderedFood # Import forms for Category and FoodItem
from .forms import VendorForm,OpeningHourForm  # Import Vendor form from current app
from accounts.forms import UserProfileForm  # Import form for UserProfile

from accounts.models import UserProfile # Import UserProfile model
from .models import Vendor, OpeningHour,DAYS  # Import OpeningHour model
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from accounts.views import check_role_vendor
from menu.models import Category,FoodItem
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse

from django.template.defaultfilters import slugify

# Get the Vendor object for the currently logged-in user
def get_vendor(request):
    vendor=Vendor.objects.get(user=request.user)
    return vendor


# 2️⃣ Vendor profile view
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorprofile(request):
    # Get the user's profile or show 404 if not found
    profile=get_object_or_404(UserProfile,user=request.user)
    # Get the vendor object for the user
    vendor=get_object_or_404(Vendor,user=request.user)

    if request.method=='POST':
        # Bind POST data to the UserProfile form
        profile_form=UserProfileForm(request.POST,request.FILES,instance=profile)
        # Bind POST data to the Vendor form
        vendor_form=VendorForm(request.POST,request.FILES,instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            # Save both forms if valid
            profile_form.save()
            vendor_form.save()
            messages.success(request,'settings updated')
            return redirect('vendorprofile')
        else:
            print(profile_form.errors)  # Print errors if forms are invalid
            print(vendor_form.errors)
    else:
        # Show forms pre-filled with existing data
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile':profile,
        'vendor':vendor,
    }
    # Pass forms and objects to template
    return render(request, 'vendor/vendorprofile.html', context)
    # Render vendor profile page



# 3️⃣ Menu builder view
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    # Get current vendor
    vendor=get_vendor(request)
    # Get all categories of this vendor
    categories=Category.objects.filter(vendor=vendor).order_by('created_at')
    context={
        'categories':categories,
    }
    return render(request,'vendor/menu_builder.html',context)
    # Render menu builder page with categories



# 4️⃣ Food items by category
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request,pk=None):
    # Get current vendor
    vendor=get_vendor(request)
    # Get category by id or 404
    category=get_object_or_404(Category,pk=pk)
    # Get all food items under this category for this vendor
    fooditems = FoodItem.objects.filter(vendor=vendor, category=category)
    context={
        'fooditems':fooditems,
        'category':category,
    }
    return render(request,'vendor/fooditems_by_category.html',context)
    # Render page with food items 



# 5️⃣ Add category
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        # Bind POST data to Category form
        form = CategoryForm(request.POST)
        if form.is_valid():
            vendor = get_vendor(request)
             # Don't save yet, assign vendor first
            category = form.save(commit=False)
            category.vendor = vendor
            try:
                category.save()  #here the category id will be generated
                # Create URL-friendly slug
                category.slug = slugify(category.category_name)+'-'+str(category.id)
                category.save()
                messages.success(request, "Category added successfully!")
                return redirect('menu_builder')
            except IntegrityError:
                # Add an error to the form
                form.add_error('category_name', 'Category already exists!')
                # Handle duplicate category name
    else:
        form = CategoryForm()  # Show empty form for GET request

    context = {
        'form': form
    }
    # Render add category page
    return render(request, 'vendor/add_category.html', context) 



# 6️⃣ Edit category
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request,pk=None):
    # Get category by id or 404
    category=get_object_or_404(Category,pk=pk)
    if request.method == 'POST':
        # Bind POST data to form with existing category
        form = CategoryForm(request.POST,instance=category)
        if form.is_valid():
            vendor = get_vendor(request)
            category = form.save(commit=False)
            category.vendor = vendor
            category.slug = slugify(category.category_name)
            try:
                category.save()
                messages.success(request, "Category Updated successfully!")
                return redirect('menu_builder')

            except IntegrityError:
                # Add an error to the form
                form.add_error('category_name', 'Category already exists!')
    else:
        form = CategoryForm(instance=category)  # Show form pre-filled with category data

    context = {
        'form': form,
        'category':category,
    }
    return render(request,'vendor/edit_category.html',context)


# 7️⃣ Delete category
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request,pk=None):
    category=get_object_or_404(Category,pk=pk)
    category.delete()
    messages.success(request,'Category has been deleted Successfully!')
    return redirect('menu_builder')
    # Delete category and redirect to menu builder



# 8️⃣ Add food item
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    # Get current vendor
    vendor = get_vendor(request)

    if request.method == 'POST':
        # Bind POST data to FoodItem form
        form = FoodItemForm(request.POST, request.FILES)

        if form.is_valid():
            food = form.save(commit=False)
            foodtitle = form.cleaned_data['food_title']
            food.vendor = vendor
            food.slug = slugify(foodtitle)

            try:
                food.save()
                messages.success(request, "Food Item added successfully!")
                return redirect('fooditems_by_category', food.category.id)

            except IntegrityError:
                form.add_error('food_title', 'Food with this name already exists!')

    else:
        form = FoodItemForm()
        # Only show this vendor's categories
        form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))


    return render(request, 'vendor/add_food.html', {'form': form})



# 9️⃣ Edit food item
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request,pk=None):
    # Get food item by id or 404
    food=get_object_or_404(FoodItem,pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST,request.FILES,instance=food)
        if form.is_valid():
            foodtitle=form.cleaned_data['food_title']
            food.vendor = get_vendor(request)
            food = form.save(commit=False)
            food.slug = slugify(foodtitle)
            try:
                food.save()
                messages.success(request, "FoodItem Updated successfully!")
                return redirect('fooditems_by_category',food.category.id)

            except IntegrityError:
                # Add an error to the form
                form.add_error('food_title', 'FoodItem already exists!')
    else:
        form = FoodItemForm(instance=food)
        # Only show this vendor's categories
        form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
        'food':food,
    }
    return render(request,'vendor/edit_food.html',context)


# 🔟 Delete food item
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request,pk=None):
    food=get_object_or_404(FoodItem,pk=pk)
    food.delete()
    messages.success(request,'Food Item has been deleted Successfully!')
    return redirect('fooditems_by_category',food.category.id)
    # Delete food item and redirect to its category page


def opening_hours(request):
    opening_hours=OpeningHour.objects.filter(vendor=get_vendor(request))
    form=OpeningHourForm()
    context={
        'form':form,
        'opening_hours':opening_hours,
    }
    return render(request,'vendor/opening_hour.html', context)

def add_opening_hours(request):
    # Handle the data and save them inside the database
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method=='POST':
            day=request.POST.get('day')
            from_hour=request.POST.get('from_hour')
            to_hour=request.POST.get('to_hour')
            is_closed=request.POST.get('is_closed')
            try:
                hour=OpeningHour.objects.create(vendor=get_vendor(request),day=day,from_hour=from_hour,to_hour=to_hour,is_closed=is_closed)
                
                # Get the day display name
                day_display = dict(DAYS).get(int(day), day)
                
                if is_closed == 'True':
                    response={'status':'success','id':hour.id,'day':day_display,'is_closed':'Closed'}
                else:
                    response={'status':'success','id':hour.id,'day':day_display,'from_hour':from_hour,'to_hour':to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response={'status':'failed','message':'Opening hour for this day already exists'}
                return JsonResponse(response)
            except Exception as e:
                response={'status':'failed','message':str(e)}
                return JsonResponse(response)

        else:
            return HttpResponse('Invalid request')
    else:
        return HttpResponse('Authentication required')

def remove_opening_hours(request, pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method=='GET':
            try:
                hour = OpeningHour.objects.get(id=pk, vendor=get_vendor(request))
                hour.delete()
                response={'status':'success','id':pk}
                return JsonResponse(response)
            except OpeningHour.DoesNotExist:
                response={'status':'failed','message':'Opening hour not found'}
                return JsonResponse(response)
            except Exception as e:
                response={'status':'failed','message':str(e)}
                return JsonResponse(response)
        else:
            return HttpResponse('Invalid request')
    else:
        return HttpResponse('Authentication required')
    
def order_detail(request,order_number):
    try:
        order=Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_food=OrderedFood.objects.filter(order=order,fooditem__vendor=get_vendor(request))

        context={
            'order':order,
            'ordered_food':ordered_food,
        }
    except:
        return redirect('vendor')
    return render(request,'vendor/order_detail.html',context)