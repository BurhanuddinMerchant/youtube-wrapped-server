from time import sleep
import boto3
from rest_framework.permissions import IsAuthenticated
import os
from api.utils import get_tokens_for_user, requestHelper
from server.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
)
from .models import AppUser
from .serializers import (
    CreateUserProfileSerializer,
    EmailVerificationSerializer,
    ForgotPasswordSerializer,
    HandleMailSerializer,
    RecaptchaVerifySerializer,
    ResetPasswordSerializer,
    TokenQuerySerializer,
    UserAvatarSerializer,
    UserProfileNameSerializer,
    UserProfileSerializer,
)
from rest_framework import generics
from rest_framework.response import Response
from django.http import HttpResponseRedirect, JsonResponse
import json
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
import requests
from rest_framework import status
from django.template.loader import get_template
from drf_yasg.utils import swagger_auto_schema

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
# Creating S3 Resource From the Session.
s3 = session.resource("s3")

# Create your views here.
class UserRegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserProfileSerializer
    throttle_scope = "anon"

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # token = Token.objects.create(user=user.user)
        token = get_tokens_for_user(user)
        host_url = os.environ["BASE_HOST_URL"]
        verification_url = f"{host_url}/api/email/verify?token={token['access']}"

        subject, from_email, to = (
            "Regarding YouTube Wrapped Account Activation",
            "ytwrpd@gmail.com",
            user.email,
        )
        text_content = "Thank You {user.username}!, please go to {verification_url} to activate your account"
        data = {"username": user.username, "verification_url": verification_url}
        html_content = get_template("verify.html").render(data)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return Response({"data": {"token": token}})


class ResendVerificationEmailAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileNameSerializer
    throttle_scope = "user"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user.is_active == False:
            host_url = os.environ["BASE_HOST_URL"]
            token = request.META["HTTP_AUTHORIZATION"][7:]
            verification_url = f"{host_url}/api/email/verify?token={token}"
            subject, from_email, to = (
                "Regarding YouTube Wrapped Account Activation",
                "ytwrpd@gmail.com",
                user.email,
            )
            text_content = "Thank You {user.username}!, please go to {verification_url} to activate your account"
            data = {"username": user.username, "verification_url": verification_url}
            html_content = get_template("verify.html").render(data)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return Response({"data": {"message": "email sent successfully"}})
        return JsonResponse({"error": "User Already Acitvated"}, status=400)


class LoadNewUserStatsIntoS3(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileNameSerializer
    throttle_scope = "user"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        liked_data = requestHelper("like", request.data["auth_token"])
        disliked_data = requestHelper("dislike", request.data["auth_token"])
        if liked_data == None or disliked_data == None:
            return JsonResponse(
                data={"error": "an error occured"}, status=400, safe=False
            )
        unprocessed = {"liked": liked_data, "disliked": disliked_data}
        object = s3.Object(AWS_STORAGE_BUCKET_NAME, f"unprocessed/{user.stats_id}.json")

        result = object.put(Body=(bytes(json.dumps(unprocessed).encode("UTF-8"))))
        user.are_stats_generated = True
        user.auth_token = request.data["auth_token"]
        user.save()
        return JsonResponse(data={"message": "Successfully Retrieved"}, safe=False)


class CheckUserStatsStatus(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileNameSerializer
    throttle_scope = "user"

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return JsonResponse(
            data={
                "data": {
                    "stats_status": user.are_stats_generated,
                    "is_active": user.is_active,
                }
            },
            safe=False,
        )


class GetUserStats(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileNameSerializer
    throttle_scope = "user"

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        content_object = s3.Object(
            AWS_STORAGE_BUCKET_NAME, f"processed/{user.stats_id}.json"
        )
        file_content = content_object.get()["Body"].read().decode("utf-8")
        json_content = json.loads(file_content)
        json_content["username"] = user.username
        return JsonResponse(data={"data": json_content}, safe=False)


class GetUserStatsTest(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileNameSerializer
    throttle_scope = "user"

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        json_content = None
        with open("test.json") as json_file:
            json_content = json.load(json_file)
        sleep(5)
        json_content["username"] = user.username
        return JsonResponse(data={"data": json_content}, safe=False)


class LoadNewUserStatsIntoS3Test(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileNameSerializer
    throttle_scope = "user"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.are_stats_generated = True
        user.save()
        sleep(10)
        return JsonResponse(data={"message": "Successfully Retrieved"}, safe=False)


class UserProfileName(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileNameSerializer

    def get(self, request, *args, **kwargs):
        user = AppUser.objects.filter(user=request.user).first()
        return JsonResponse(
            data={"data": {"username": user.username, "avatar": user.avatar}},
            safe=False,
        )


class HandleMail(generics.GenericAPIView):
    permission_classes = ()
    serializer_class = HandleMailSerializer
    throttle_scope = "anon"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Email = serializer.save()
        name = Email["name"]
        message = Email["message"]
        email = Email["email"]
        send_mail(
            f"Regarding Youtube Wrapped from ,{name} email : {email}",
            message,
            email,
            ["ytwrpd@gmail.com"],
            fail_silently=False,
        )
        return JsonResponse(data={"message": "successful"})


class EmailVerification(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    throttle_scope = "user"

    @swagger_auto_schema(
        query_serializer=TokenQuerySerializer,
        security=[],
        operation_id="Verify Email",
        operation_description="This endpoint is used to verify the email",
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = User.objects.get(id=user_id)
            app_user = AppUser.objects.filter(user=user).first()
            if app_user.is_active == False:
                app_user.is_active = True
                subject, from_email, to = (
                    "Regarding YouTube Wrapped Account Activation",
                    "ytwrpd@gmail.com",
                    user.email,
                )
                text_content = f"Thank You {user.username}!, Your account is verified. You can now go ahead and generate your wrap"
                data = {"username": user.username}
                html_content = get_template("verify_ack.html").render(data)
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                app_user.save()
                return HttpResponseRedirect(
                    redirect_to="https://youtubewrapped.ml/login"
                )
            else:
                return HttpResponseRedirect(
                    redirect_to="https://youtubewrapped.ml/login"
                )
        except Exception:
            return JsonResponse(
                data={
                    "message": "User does not exist or The verification link has expired, please login and reavail the verification email"
                },
                status=404,
            )


class RecaptchaVerifyAPI(generics.GenericAPIView):
    serializer_class = RecaptchaVerifySerializer
    throttle_scope = "anon"

    @swagger_auto_schema(
        query_serializer=TokenQuerySerializer,
        security=[],
        operation_id="Recaptcha Verification",
        operation_description="This endpoint is used for recaptcha verification",
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
        url = "https://www.google.com/recaptcha/api/siteverify"
        result = requests.post(
            url=url, params={"secret": RECAPTCHA_SECRET_KEY, "response": token}
        )
        result = result.json()
        return JsonResponse(data={"verified": result["success"]})


class UserProfileAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer
    throttle_scope = "user"

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        resp = {
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "are_stats_generated": user.are_stats_generated,
            "date_joined": user.user.date_joined,
            "avatar": user.avatar,
        }
        return JsonResponse(data={"user": resp})

    def delete(self, request, *args, **kwargs):
        subject, from_email, to = (
            "Regarding YouTube Wrapped Profile Deletion",
            "ytwrpd@gmail.com",
            request.user.email,
        )
        text_content = "Sad to see you go, {request.user.username} :( .Your Youtube Wrapped Profile has been deleted successfully. Hope to see you back very soon :)"
        data = {"username": request.user.username}
        html_content = get_template("delete.html").render(data)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        request.user.delete()
        return JsonResponse({"message": "Account Deleted Successfully"})


class ResetPasswordAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ResetPasswordSerializer
    throttle_scope = "user"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset = serializer.save()
        if reset:
            return JsonResponse(data={"user": "Password Reset Successful"})
        else:
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordAPI(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    throttle_scope = "anon"

    def post(self, request, *args, **kwargs):
        return JsonResponse(data={"message": "Password Reset Successful"})


class UserAvatarAPI(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserAvatarSerializer
    throttle_scope = "user"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse(data={"message": "avatar updated successfully"})


class TestThrottleAPI(generics.GenericAPIView):
    throttle_scope = "anon"

    def get(self, request, *args, **kwargs):
        return JsonResponse(data={"status": "OK"})


class TestEmailTemplate(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        subject, from_email, to = "hello", "from@example.com", "ytwrpd@gmail.com"
        text_content = "This is an important message."
        data = {
            "title": "This is the dynamic title",
            "url": "https://youtubewrapped.ml",
        }
        html_content = get_template("test.html").render(data)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return JsonResponse(data={"status": "OK"})
