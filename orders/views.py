from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order, OrderedFood, Payment
import simplejson as json
from .utils import generate_order_number


def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('marketplace')

    cart_amounts = get_cart_amounts(request)
    subtotal = cart_amounts['subtotal']
    total_tax = cart_amounts['tax']
    grand_total = cart_amounts['grand_total']
    tax_data = cart_amounts['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST.get('payment_method')
            order.save()

            # Generate order number
            order.order_number = generate_order_number(order.id)
            order.save()

            context = {
                'order': order,
                'cart_items': cart_items,
                'subtotal': subtotal,
                'tax_dict': tax_data,
                'grand_total': grand_total,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)

    return render(request, 'orders/place_order.html')


def payments(request):
    # Check AJAX POST request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':

        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        # Get order
        order = Order.objects.get(user=request.user, order_number=order_number)

        # Save payment
        payment = Payment.objects.create(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status,
        )

        # Update order
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move cart items to OrderedFood
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            OrderedFood.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                fooditem=item.fooditem,
                quantity=item.quantity,
                price=item.fooditem.price,
                amount=item.fooditem.price * item.quantity
            )

        # Clear cart
        #cart_items.delete()

        # IMPORTANT: send redirect URL
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id,
            'redirect_url': f"/order-complete/?order_no={order_number}&trans_id={transaction_id}"
        }

        return JsonResponse(response)

    return HttpResponse('Payments view')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(
            order_number=order_number,
            payment__transaction_id=transaction_id,
            is_ordered=True
        )

        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal=0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data=json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal':subtotal,
            'tax_data':tax_data,
        }
        return render(request, 'orders/order_complete.html', context)

    except Order.DoesNotExist:
        return redirect('home')
