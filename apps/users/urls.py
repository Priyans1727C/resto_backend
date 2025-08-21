from django.urls import path
from .views import UserView,UserRegisterView,UserLoginView,UserChangePasswordView,AccessTokenRefreshView,UserLogoutView,VerifyEmailView,ForgotPasswordView,ResetPasswordView



urlpatterns = [
    path("auth/me/",UserView.as_view()),
    path("auth/refresh/", AccessTokenRefreshView.as_view(), name="refresh"),
    path("auth/register/", UserRegisterView.as_view(), name="register"),
    path('auth/login/', UserLoginView.as_view()),
    path("auth/change-password/", UserChangePasswordView.as_view(), name="change_password"),
    path("auth/logout/", UserLogoutView.as_view(), name="logout"),
    path("auth/verify_email/<str:uidb64>/<str:token>/",VerifyEmailView.as_view(),name="verify_email"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("auth/reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="password_reset_confirm"),
]