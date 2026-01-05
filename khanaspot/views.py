from django.shortcuts import render
from django.http import HttpResponse
from vendor .models import Vendor

# Define a view function called 'home' that takes a request object
def home(request):
    # Query the Vendor model to get vendors that are approved and whose user accounts are active
    # Limit the results to the first 8 vendors
    vendors=Vendor.objects.filter(is_approved=True,user__is_active=True)[:8]
    # Prepare context data to pass to the template
    context={
        'vendors':vendors,
    }
    return render(request,'home.html',context)   # Render the 'home.html' template with the given context