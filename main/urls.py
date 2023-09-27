from django.urls import path

from . import views

app_name = "main"
urlpatterns = [
    path("home", views.HomeView.as_view(), name="home"),
    path("product_list/", views.ProductListView.as_view(), name="product_list"),
    path(
        "product_detail/<int:pk>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),
    path("like/<int:pk>/", views.product_like, name="like"),
    path("unlike/<int:pk>/", views.product_unlike, name="unlike"),
    path("product_sell/", views.product_sell, name="product_sell"),
    path(
        "purchase_confirmation/<int:pk>/",
        views.PurchaseConfirmationView.as_view(),
        name="purchase_confirmation",
    ),
    path(
        "purchase_procedure/address/", views.InputAddressView.as_view(), name="address"
    ),
    path(
        "purchase_procedure/payment/", views.InputPaymentView.as_view(), name="payment"
    ),
    path(
        "purchase_procedure/final_confirmation/",
        views.CreateCheckoutView.as_view(),
        name="final_confirmation",
    ),
    path(
        "change_delivery_status/<int:pk>/",
        views.change_delivery_status,
        name="change_delivery_status",
    ),
    path("delete_product/<int:pk>/", views.delete_product, name="delete_product"),
    path(
    "account/",
    views.AccountView.as_view(),
    name="account",
    ),
    path(
        "terms/",
        views.TermsView.as_view(),
        name="terms",
    ),
    path(
        "privacy_policy/",
        views.PrivacyPolicyView.as_view(),
        name="privacy_policy",
    ),
    path(
        "account_delete/",
        views.AccountDeleteView.as_view(),
        name="account_delete",
    ),
    path(
        "account_delete_done/",
        views.AccountDeleteDoneView.as_view(),
        name="account_delete_done",
    ),
    path(
    "account_detail/<int:pk>",
    views.AccountDetailView.as_view(),
    name="account_detail",
    ),
    path("liked_list/", views.ProductLikedListView.as_view(), name="liked_list"),
    path(
        "exhibited_list/", views.ProductExibitListView.as_view(), name="exhibited_list"
    ),
    path(
    "purchased_list",
    views.ProductPurchasedListView.as_view(),
    name="purchased_list",
    ),
    path(
    "account_update",
    views.AccountUpdateView.as_view(),
    name="account_update",
    ),
    path("notification/", views.NotificationView.as_view(), name="notification"),
]