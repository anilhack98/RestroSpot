import datetime

from django.db.models import Count, Max

from menu.models import FoodItem
from vendor.models import Vendor
from .models import OrderedFood


def generate_order_number(pk):
    current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    order_number = current_datetime + str(pk)
    return order_number


def get_recommended_vendors_for_user(user, limit=8):
    """
    Recommend vendors based on the user's order history.

    Strategy:
    - If the user is authenticated and has past orders (via OrderedFood),
      rank vendors by how often the user has ordered their food.
    - If the user has no history, fall back to globally popular vendors
      ranked by total number of ordered items.
    """
    # 1. Base query: Only consider vendors that are approved and whose owner's account is active
    base_qs = Vendor.objects.filter(is_approved=True, user__is_active=True)

    # 2. If the user is a guest (not logged in), return the most recently added vendors
    if not getattr(user, "is_authenticated", False):
        return base_qs.order_by("-created_at")[:limit]

    # 3. For logged-in users, find vendors they have ordered from before
    # We group their past orders by vendor and find the most recent order date for each
    user_vendor_counts = (
        OrderedFood.objects.filter(user=user)
        .values("fooditem__vendor")
        .annotate(last_order=Max("created_at"))
        .order_by("-last_order")  # Sort so the most recently ordered vendor comes first
    )

    # 4. Extract just the vendor IDs from the query results, ignoring any null values
    vendor_ids = [row["fooditem__vendor"] for row in user_vendor_counts if row["fooditem__vendor"]]

    if vendor_ids:
        # 5. We need to fetch the actual Vendor objects, but the database might not return them 
        # in the exact sorted order we want. So we map each ID to its correct rank index.
        vendor_order = {vid: index for index, vid in enumerate(vendor_ids)}
        vendors = list(
            base_qs.filter(id__in=vendor_ids)
        )
        # Sort the fetched vendors exactly as they appeared in our recent-order ranking
        vendors.sort(key=lambda v: vendor_order.get(v.id, len(vendor_order)))
        return vendors[:limit]

    # 6. Fallback: If the logged-in user has never ordered anything, we recommend the 
    # most globally popular vendors across all users by counting total items ordered.
    global_vendor_counts = (
        OrderedFood.objects.values("fooditem__vendor")
        .annotate(order_count=Count("id"))  # Count how many times items from this vendor were ordered
        .order_by("-order_count")           # Sort from highest count to lowest
    )
    
    # 7. Extract the list of vendor IDs for globally popular vendors
    global_vendor_ids = [row["fooditem__vendor"] for row in global_vendor_counts if row["fooditem__vendor"]]

    # If there are no orders at all in the database, return recently created vendors
    if not global_vendor_ids:
        return base_qs.order_by("-created_at")[:limit]

    # 8. Fetch the Vendor objects and apply the correct popularity ranking
    global_order = {vid: index for index, vid in enumerate(global_vendor_ids)}
    vendors = list(
        base_qs.filter(id__in=global_vendor_ids)
    )
    vendors.sort(key=lambda v: global_order.get(v.id, len(global_order)))
    
    # 9. Return up to the requested limit (e.g., top 8)
    return vendors[:limit]


def get_recommended_fooditems_for_user(user, limit=8):
    """
    Recommend food items based on the user's recent purchase history.

    Strategy:
    - If the user is authenticated, rank food items by the most recent time
      the user ordered them (recency-based).
    - If the user has no history, fall back to globally popular items.
    """
    # 1. Base query: Only consider food items that are currently marked as available
    base_qs = FoodItem.objects.filter(is_available=True)

    # 2. If the user is a guest (not logged in), return the most recently added food items
    if not getattr(user, "is_authenticated", False):
        return base_qs.order_by("-created_at")[:limit]

    # 3. For logged-in users, find the food items they personally ordered in the past
    # and rank them by the most recent order date
    user_food_counts = (
        OrderedFood.objects.filter(user=user)
        .values("fooditem")
        .annotate(last_order=Max("created_at"))
        .order_by("-last_order")  # Most recently ordered items come first
    )

    # 4. Extract the IDs of these previously ordered food items
    food_ids = [row["fooditem"] for row in user_food_counts if row["fooditem"]]

    if food_ids:
        # 5. Fetch the actual FoodItem objects and sort them to match the recency ranking
        food_order = {fid: index for index, fid in enumerate(food_ids)}
        items = list(base_qs.filter(id__in=food_ids))
        items.sort(key=lambda item: food_order.get(item.id, len(food_order)))
        return items[:limit]

    # 6. Fallback: If the user has never ordered anything, recommend the
    # most globally popular food items (the items ordered the most times by everyone)
    global_food_counts = (
        OrderedFood.objects.values("fooditem")
        .annotate(order_count=Count("id"))  # Count total times this exact food item was ordered
        .order_by("-order_count")           # Sort from mostly highly ordered to least
    )
    
    # 7. Extract the IDs of globally popular food items
    global_food_ids = [row["fooditem"] for row in global_food_counts if row["fooditem"]]

    # If there are no orders at all in the database, return recently created food items
    if not global_food_ids:
        return base_qs.order_by("-created_at")[:limit]

    # 8. Fetch the FoodItem objects and apply the correct popularity ranking
    global_order = {fid: index for index, fid in enumerate(global_food_ids)}
    items = list(base_qs.filter(id__in=global_food_ids))
    items.sort(key=lambda item: global_order.get(item.id, len(global_order)))
    
    # 9. Return up to the requested limit (e.g., top 8)
    return items[:limit]

