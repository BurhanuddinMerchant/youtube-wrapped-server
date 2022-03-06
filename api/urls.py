from django.urls import path
from .views import *

urlpatterns = [
    path("register", UserRegistrationAPI.as_view()),
    path("generate", LoadNewUserStatsIntoS3.as_view()),
    path('profile',GetUserProfile.as_view()),
    path("stats",GetUserStats.as_view()),
    path("check",CheckUserStatsStatus.as_view()),
    path('email',HandleMail.as_view()),
    path("test/stats",GetUserStatsTest.as_view()),
    path("test/generate", LoadNewUserStatsIntoS3.as_view())
]
