from django.urls import path

from . import views

urlpatterns = [
    path(
        "signup/",
        views.CustomSignupView.as_view(),
        name="signup",
    ),
    path("email/change/", views.EmailChangeView.as_view(), name="account_email_change"),
    path(
        "email/change/done/",
        views.EmailChangeDoneView.as_view(),
        name="account_email_change_done",
    ),
    path(
        "password/change/",
        views.CustomPasswordChangeView.as_view(),
        name="change_password",
    ),
]