from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Kalau Google login pakai email yang udah punya User (misal dari
        signup OTP), sambungkan SocialAccount ke User lama itu — jangan
        biarkan allauth coba bikin User baru yang bakal collision.
        """
        if sociallogin.is_existing:
            return

        email = sociallogin.user.email
        if not email:
            return

        existing_user = User.objects.filter(email__iexact=email).first()
        if existing_user:
            sociallogin.connect(request, existing_user)