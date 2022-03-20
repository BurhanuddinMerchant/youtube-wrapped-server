from rest_framework import serializers
from django.contrib.auth.models import User
from .models import AppUser


class CreateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser

        fields = (
            "email",
            "password",
            "username",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        user_profile = AppUser(
            user=user,
            username=validated_data["username"],
            email=validated_data["email"],
            is_active=False,
        )
        user_profile.save()
        return user


class UserProfileSerializer(serializers.Serializer):
    def create(self, validated_data):
        request = self.context.get("request")
        user = AppUser.objects.filter(user=request.user).first()
        return user


class EmailVerificationSerializer(serializers.Serializer):
    def create(self, validated_data):
        request = self.context.get("request")
        token = request.query_params.get("token")
        return token


class HandleMailSerializer(serializers.Serializer):
    class Meta:
        fields = ("name", "message", "email")

    def create(self, validated_data):
        request = self.context.get("request")
        name = request.data["name"]
        message = request.data["message"]
        email = request.data["email"]
        Email = {"name": name, "message": message, "email": email}
        return Email


class RecaptchaVerifySerializer(serializers.Serializer):
    def create(self, validated_data):
        request = self.context.get("request")
        token = request.query_params.get("token")
        return token
