from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *

urlpatterns = [
    path("register", UserRegistrationAPI.as_view(), name="signup"),
    path("generate", LoadNewUserStatsIntoS3.as_view(), name="generate_stats"),
    path("profile", UserProfileAPI.as_view(), name="user_profile"),
    path("profile/name", UserProfileName.as_view(), name="user_profile_name"),
    path("stats", GetUserStats.as_view(), name="user_stats"),
    path("check", CheckUserStatsStatus.as_view(), name="check_user_status"),
    path("email", HandleMail.as_view(), name="feedback"),
    path("email/verify", EmailVerification.as_view(), name="verify_email"),
    path(
        "email/resend", ResendVerificationEmailAPI.as_view(), name="verify_email_resend"
    ),
    path("token", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("recaptcha", RecaptchaVerifyAPI.as_view(), name="verify_recaptcha"),
    path("test/stats", GetUserStatsTest.as_view()),
    path("test/generate", LoadNewUserStatsIntoS3Test.as_view()),
    # path("test/throttle", TestThrottleAPI.as_view()),
    # path("test/email", TestEmailTemplate.as_view(), name="test_email_template"),
]
