from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationToken:
    generator = PasswordResetTokenGenerator()
    
    @staticmethod
    def create(user):
        return EmailVerificationToken.generator.make_token(user)
    
    @staticmethod
    def verify(user, token):
        return EmailVerificationToken.generator.check_token(user,token)
    