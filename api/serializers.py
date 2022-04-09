from asyncio import constants
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


class UserProfileNameSerializer(serializers.Serializer):
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
    name = serializers.CharField(max_length=256)
    email = serializers.EmailField()
    message = serializers.CharField()

    def create(self, validated_data):
        name = validated_data["name"]
        message = validated_data["message"]
        email = validated_data["email"]
        Email = {"name": name, "message": message, "email": email}
        return Email


class RecaptchaVerifySerializer(serializers.Serializer):
    def create(self, validated_data):
        request = self.context.get("request")
        token = request.query_params.get("token")
        return token


class UserProfileSerializer(serializers.Serializer):
    def create(self, validated_data):
        request = self.context.get("request")
        user = AppUser.objects.filter(user=request.user).first()
        return user


class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=256)
    new_password = serializers.CharField(max_length=256)

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        if not user.check_password(validated_data["old_password"]):
            return False
        else:
            user.set_password(validated_data["new_password"])
            user.save()
        return True


class ForgotPasswordSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass


class UserAvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField(max_length=10)

    def create(self, validated_data):
        request = self.context.get("request")
        user = AppUser.objects.filter(user=request.user).first()
        user.avatar = validated_data["avatar"]
        user.save()
        return user


class TokenQuerySerializer(serializers.Serializer):
    token = serializers.CharField(max_length=512)

    def create(self, validated_data):
        return validated_data["token"]
