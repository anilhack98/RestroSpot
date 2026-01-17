let autocomplete;

function initAutoComplete() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById('id_address'),
        {
            types: ['address'],
            componentRestrictions: { country: ['NP'] }
        }
    );

    autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged() {
    const place = autocomplete.getPlace();

    if (!place.geometry) {
        document.getElementById('id_address').placeholder = "Start typing...";
        return;
    }

    // Set lat & lng
    $('#id_latitude').val(place.geometry.location.lat());
    $('#id_longitude').val(place.geometry.location.lng());

    let pinFound = false;

    for (let i = 0; i < place.address_components.length; i++) {
        const component = place.address_components[i];

        if (component.types.includes('country')) {
            $('#id_country').val(component.long_name);
        }

        if (component.types.includes('administrative_area_level_1')) {
            $('#id_state').val(component.long_name);
        }

        if (component.types.includes('locality')) {
            $('#id_city').val(component.long_name);
        }

        if (component.types.includes('postal_code')) {
            $('#id_pin_code').val(component.long_name);
            pinFound = true;
        }
    }

    if (!pinFound) {
        $('#id_pin_code').val('');
    }
}



$(document).ready(function(){
    // add to cart
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
          
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if(response.status =='login_required'){
                    Swal(response.message,'','info').then(function(){
                        window.location='/login'
                    })
                }if(response.status=='Failed'){
                    Swal(response.message,'','error')
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty);

                    // SUbtotal,tax,total
                    applyCartAmounts(
                        response.cart_amounts['subtotal'],
                        response.cart_amounts['tax'],
                        response.cart_amounts['grand_total']
                    )
                }
            }
        })
    })


    // place the cart item quantity on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        $('#'+the_id).html(qty)
    }) 

    // decrease cart
     $('.decrease_cart').on('click', function(e){
        e.preventDefault();
        
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');
          
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if(response.status =='login_required'){
                    Swal(response.message,'','info').then(function(){
                        window.location='/login'
                    })
                }else if(response.status=='Failed'){
                    Swal(response.message,'','error')
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty);

                    applyCartAmounts(
                        response.cart_amounts['subtotal'],
                        response.cart_amounts['tax'],
                        response.cart_amounts['grand_total']
                    )

                    if(window.location.pathname == '/cart/'){
                        // Remove the cart item automatically if qty is decreased to 0
                    removeCartItem(response.qty, cart_id);
                    checkEmptyCart();

                    }
                }
                
            }
        })
    })


    // DELETE CART ITEM
    $('.delete_cart').on('click', function(e){
        e.preventDefault();
        
        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if(response.status=='Failed'){
                    swal(response.message,'','error')
                }else{
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status,response.message,'success')

                    applyCartAmounts(
                        response.cart_amounts['subtotal'],
                        response.cart_amounts['tax'],
                        response.cart_amounts['grand_total']
                    ) 

                    removeCartItem(0,cart_id)
                    checkEmptyCart();
                }
            }
        })
    })

    // Delete the cart element if the quantity is 0
    function removeCartItem(cartItemQty,cart_id){
        if(cartItemQty <= 0){
            // remove the cart item element
            document.getElementById("cart-item-"+cart_id).remove()

        }

    }

    // Check if the cart is empty
    function checkEmptyCart(){
        var cart_counter=document.getElementById('cart_counter').innerHTML
        if(cart_counter == 0){
            document.getElementById("empty_cart").style.display = "block";
        }
    }

    // Apply cart amounts
    function applyCartAmounts(SUbtotal,tax,grand_total){
        if (window.location.pathname == '/cart/'){
            $('#subtotal').html(SUbtotal)
        $('#tax').html(tax)
        $('#total').html(grand_total)

        }
    }

    $('.add_hour').on('click',function(e){
        e.preventDefault();
        var day=document.getElementById('id_day').value
        var from_hour=document.getElementById('id_from_hour').value
        var to_hour=document.getElementById('id_to_hour').value
        var is_closed=document.getElementById('id_is_closed').checked
        var csrf_token=$('input[name=csrfmiddlewaretoken]').val() // In Jquery if we want to take value we need to use Val function
        var url=document.getElementById('add_hour_url').value

        console.log(day,from_hour,to_hour,is_closed,csrf_token)

        if(is_closed){
            is_closed='True'
            condition="day != ''"
        }else{
            is_closed='False'
            condition="day != '' && from_hour != '' && to_hour != ''"
        }

        if(eval(condition)){
            $.ajax({
                type:'POST',
                url:url,
                data:{
                    'day':day,
                    'from_hour':from_hour,
                    'to_hour':to_hour,
                    'is_closed':is_closed,
                    'csrfmiddlewaretoken':csrf_token,
                },
                success:function(response){
                    if(response.status=='success'){
                        html='<tr><td><b>'+response.day+'</b></td><td>'+ response.from_hour+'-'+ response.to_hour+'</td><td><a href="#">Remove</a></td></tr>';
                        $(".opening_hours").append(html)
                        document.getElementById("opening_hours").reset()
                    }else{
                        swal(response.message,'',"error")
                    }
                }
            })
        }else{
            swal('Please fill all fields','','info')
        }
    })
    // Documentary ready close


});