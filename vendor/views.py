from django.shortcuts import render

def vendorprofile(request):
    return render(request,'vendor/vendorprofile.html')