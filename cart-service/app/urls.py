from django.urls import path

from .views import (
    AddToCartView,
    CartDetailView,
    ClearCartView,
    InternalCartDetailView,
    InternalClearCartView,
    RemoveCartItemView,
    UpdateCartView,
)

urlpatterns = [
    path("cart/add", AddToCartView.as_view(), name="cart-add"),
    path("cart/", CartDetailView.as_view(), name="cart-detail"),
    path("cart/update", UpdateCartView.as_view(), name="cart-update"),
    path("cart/remove", RemoveCartItemView.as_view(), name="cart-remove"),
    path("cart/clear", ClearCartView.as_view(), name="cart-clear"),
    path("internal/cart/<int:user_id>/", InternalCartDetailView.as_view(), name="internal-cart-detail"),
    path("internal/cart/<int:user_id>/clear", InternalClearCartView.as_view(), name="internal-cart-clear"),
]
