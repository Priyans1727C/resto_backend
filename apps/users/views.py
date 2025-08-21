from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status
from .serializers import UserSafeSerializer,UpdateUserSerializer,UserRegisterSerializer,RoleTokenObtainPairSerializer,UserChangePassword,UserEmailSerializer,ResetPasswordSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from django.contrib.auth import authenticate,login
from rest_framework.authtoken.models import Token 
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .auth import set_refresh_cookie,clear_refresh_cookie
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.services.email_service import EmailService
from apps.users.services.verification_service import VerificationService
from django.utils.http import urlsafe_base64_decode


# Create your views here.

User = get_user_model()


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        ser = UserSafeSerializer(request.user)
        return Response(ser.data)
    def patch(self,request):
        ser = UpdateUserSerializer(request.user, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)
    
    

class UserRegisterView(APIView):
    def post(self,request):
        ser = UserRegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        VerificationService.send_verification_email(request,user)
        return Response(
            {
                "detail":"User registered successfully. Please verify your email.",
                "user":UserSafeSerializer(user).data,
            },
            status=status.HTTP_201_CREATED
        )
        
    

class VerifyEmailView(APIView):
    def get(self,request,uidb64,token):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail":"Invalid or expired link"},status=status.HTTP_400_BAD_REQUEST)

        if VerificationService.activate_user(user,token):
             return Response({"Email verified successfully!"})
        
        return Response({"detail":"Invalid or expired link"},status=status.HTTP_400_BAD_REQUEST)
"""
#basic session base login

class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request,user)
            return Response({'token': "nicelydone"})
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
"""

class ForgotPasswordView(APIView):
    serializer_class=UserEmailSerializer 
    def post(self,request,*args, **kwargs):
        ser = self.serializer_class(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=ser.validated_data['email'])
            VerificationService.send_verification_password_email(request,user)
        except Exception as e:
            pass
        return Response({"detail": "If this email exists, a reset link has been sent."})

class ResetPasswordView(APIView):
    def post(self,request,uidb64,token, **kwargs):
        ser = ResetPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail":"Invalid or expired link"}, status=status.HTTP_400_BAD_REQUEST)

        if VerificationService.verify_token(user,token):
            user.set_password(ser.validated_data["new_password"])
            user.save(update_fields = ["password"])
            return Response({"detail":"Password changed"},status=200)

        return Response({"detail":"Invalid or expired link"}, status=status.HTTP_400_BAD_REQUEST)
    
        

class AccessTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        request.data["refresh"] = request.COOKIES.get("refresh_token")
        return super().post(request, *args, **kwargs)


class UserLoginView(TokenObtainPairView):
    serializer_class = RoleTokenObtainPairSerializer
    def post(self, request,*args,**kargs):
        res = super().post(request,*args,**kargs)
        refresh = res.data.pop("refresh",None)
        if refresh:
            set_refresh_cookie(res,refresh)
        return res
        
        
class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    # serializer_class = UserChangePassword
    def post(self,request):
        ser = UserChangePassword(data = request.data)
        ser.is_valid(raise_exception=True)
        if not request.user.check_password(ser.validated_data["old_password"]):
            return Response({"detail":"Old password is incorrect"}, status=400)
        request.user.set_password(ser.validated_data["new_password"])
        request.user.save(update_fields = ["password"])
        return Response({"detail":"Password changed"},status=200)
    
    
class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        rt = request.COOKIES.get("refresh_token")
        if rt:
            try:
                RefreshToken(rt).blacklist()
            except:
                pass
        res = Response({"Detail":"Logout Sucessfull"})
        clear_refresh_cookie(res)
        return res
                