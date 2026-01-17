from .models import Cart,Tax  # Import the Cart model from current app
from menu .models import FoodItem


# Define a function to get the total number of items in the user's cart
def get_cart_counter(request):
    cart_count=0    # Initialize the cart count to 0
    if request.user.is_authenticated:   # Check if the user is logged in
        try:
            # Get all cart items for the logged-in user
            cart_item=Cart.objects.filter(user=request.user)
            if cart_item:  # If the user has items in the cart
                for cart_item in cart_item:   # Loop through each cart item and add its quantity to cart_count
                    cart_count+= cart_item.quantity
            else:
                cart_count=0  # If no items, cart count remains 0
                    
        except:
            cart_count=0    # In case of any error, set cart count to 0
    return dict(cart_count=cart_count)    # Return the cart count as a dictionary

# Made function of get_cart_amounts with variable 0
def get_cart_amounts(request):
    subtotal=0
    tax=0
    grand_total=0
    tax_dict={}
    if request.user.is_authenticated:  # Check User Authentication
        cart_items=Cart.objects.filter(user=request.user)  # get the cart item of logged in user
        for item in cart_items:  # looping through all cart item
            fooditem=FoodItem.objects.get(pk=item.fooditem.id)  # Getting the fooditem with their PK
            subtotal += (fooditem.price * item.quantity)  #subtotal=subtotal + (fooditem.price * item.quantity)

            get_tax=Tax.objects.filter(is_active=True)
            for i in get_tax:
                tax_type=i.tax_type
                tax_percentage=i.tax_percentage
                tax_amount=round((tax_percentage*subtotal)/100,2)
                tax_dict.update({tax_type:{str(tax_percentage):tax_amount}})

            tax=sum(x for key in tax_dict.values() for x in key.values())

            grand_total=subtotal + tax
    return dict(subtotal=subtotal,tax=tax,grand_total=grand_total,tax_dict=tax_dict) 