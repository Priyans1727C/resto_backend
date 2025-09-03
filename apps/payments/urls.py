from django.urls import path
from . import views

urlpatterns = [
    path("create/",views.CreatePayemntView.as_view(),name="create-payment"),
    path("getPayments",views.PaymentDetaildView.as_view(),name="all-payments"),
    path("healthz/", lambda r: __import__("django.http").http.JsonResponse({"ok": True})),
]
