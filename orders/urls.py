from django.urls import path
from .import views

urlpatterns=[
    path('place_order/',views.place_order,name='place_order'),
    path('payments/', views.payments,name='payments'),
    path('order_complete/',views.order_complete,name='order_complete'),
    path('cancel_order/<int:order_number>/', views.cancel_order, name='cancel_order'),
    path('mark_order_failed/<int:order_number>/', views.mark_order_failed, name='mark_order_failed'),
]