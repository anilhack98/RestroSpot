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
    base_qs = Vendor.objects.filter(is_approved=True, user__is_active=True)

    if not getattr(user, "is_authenticated", False):
        return base_qs.order_by("-created_at")[:limit]

    # Vendors ranked by most recent order time for this user
    user_vendor_counts = (
        OrderedFood.objects.filter(user=user)
        .values("fooditem__vendor")
        .annotate(last_order=Max("created_at"))
        .order_by("-last_order")
    )

    vendor_ids = [row["fooditem__vendor"] for row in user_vendor_counts if row["fooditem__vendor"]]

    if vendor_ids:
        # Preserve the ranking defined by vendor_ids
        vendor_order = {vid: index for index, vid in enumerate(vendor_ids)}
        vendors = list(
            base_qs.filter(id__in=vendor_ids)
        )
        vendors.sort(key=lambda v: vendor_order.get(v.id, len(vendor_order)))
        return vendors[:limit]

    # Fallback: globally popular vendors by total ordered items
    global_vendor_counts = (
        OrderedFood.objects.values("fooditem__vendor")
        .annotate(order_count=Count("id"))
        .order_by("-order_count")
    )
    global_vendor_ids = [row["fooditem__vendor"] for row in global_vendor_counts if row["fooditem__vendor"]]

    if not global_vendor_ids:
        return base_qs.order_by("-created_at")[:limit]

    global_order = {vid: index for index, vid in enumerate(global_vendor_ids)}
    vendors = list(
        base_qs.filter(id__in=global_vendor_ids)
    )
    vendors.sort(key=lambda v: global_order.get(v.id, len(global_order)))
    return vendors[:limit]


def get_recommended_fooditems_for_user(user, limit=8):
    """
    Recommend food items based on the user's recent purchase history.

    Strategy:
    - If the user is authenticated, rank food items by the most recent time
      the user ordered them (recency-based).
    - If the user has no history, fall back to globally popular items.
    """
    base_qs = FoodItem.objects.filter(is_available=True)

    if not getattr(user, "is_authenticated", False):
        return base_qs.order_by("-created_at")[:limit]

    user_food_counts = (
        OrderedFood.objects.filter(user=user)
        .values("fooditem")
        .annotate(last_order=Max("created_at"))
        .order_by("-last_order")
    )

    food_ids = [row["fooditem"] for row in user_food_counts if row["fooditem"]]

    if food_ids:
        food_order = {fid: index for index, fid in enumerate(food_ids)}
        items = list(base_qs.filter(id__in=food_ids))
        items.sort(key=lambda item: food_order.get(item.id, len(food_order)))
        return items[:limit]

    # Fallback: globally popular food items
    global_food_counts = (
        OrderedFood.objects.values("fooditem")
        .annotate(order_count=Count("id"))
        .order_by("-order_count")
    )
    global_food_ids = [row["fooditem"] for row in global_food_counts if row["fooditem"]]

    if not global_food_ids:
        return base_qs.order_by("-created_at")[:limit]

    global_order = {fid: index for index, fid in enumerate(global_food_ids)}
    items = list(base_qs.filter(id__in=global_food_ids))
    items.sort(key=lambda item: global_order.get(item.id, len(global_order)))
    return items[:limit]

