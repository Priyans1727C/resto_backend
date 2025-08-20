from .token_service import EmailVerificationToken
from .email_service import EmailService

from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from apps.users.utils.email_templates import verification_email_template


class VerificationService:
    @staticmethod
    def send_verification_email(request,user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = EmailVerificationToken.create(user)
        verify_url = request.build_absolute_uri(
            reverse("verify_email",kwargs={"uidb64":uid,"token":token})
        )
        
        text_content,html_content = verification_email_template(user,verify_url)
        EmailService.send_email(
            subject="Verify your Email",
            to_email=user.email,
            text_content=text_content,
            html_content=html_content
        )
        
    @staticmethod
    def activate_user(user,token):
        if EmailVerificationToken.verify(user,token):
            # user.is_active=True
            user.is_email_verified=True
            user.save()
            return True
        return False