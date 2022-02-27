from distutils.log import error
from inspect import getmembers
import boto3
from rest_framework.permissions import IsAuthenticated

from api.utils import requestHelper
from server.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME

from .models import AppUser
from .serializers import  CreateUserProfileSerializer
from rest_framework import generics
from .auth import BearerToken
from rest_framework.response import Response
from django.http import JsonResponse
from django.core import serializers
from rest_framework.authtoken.models import Token
import json
from django.core import serializers

session = boto3.Session(
aws_access_key_id=AWS_ACCESS_KEY_ID,
aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
#Creating S3 Resource From the Session.
s3 = session.resource('s3')

# Create your views here.
class UserRegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserProfileSerializer

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user.user)
        return Response({"user": "User", "data": {"token": token.key}})

class LoadNewUserStatsIntoS3(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BearerToken,)
    def post(self,request,*args,**kwargs):
        user = AppUser.objects.filter(user=request.user).first()
        liked_data = requestHelper("like",request.data["auth_token"]);
        disliked_data = requestHelper("dislike",request.data["auth_token"]);
        if liked_data==None or disliked_data==None:
            return JsonResponse(data={"error":"an error occured"},status=400,safe=False)
        unprocessed = {"liked":liked_data,"disliked":disliked_data}
        object = s3.Object(AWS_STORAGE_BUCKET_NAME, f'unprocessed/{user.stats_id}.json')

        result = object.put(Body=(bytes(json.dumps(unprocessed).encode('UTF-8'))))
        user.are_stats_generated = True;
        user.auth_token = request.data["auth_token"];
        user.save();
        return JsonResponse(data={"message":"Successfully Retrieved"}, safe=False)

class CheckUserStatsStatus(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BearerToken,)
    def get(self,request,*args,**kwargs):
        user = AppUser.objects.filter(user=request.user).first()
        return JsonResponse(data={"data":{"status":user.are_stats_generated}}, safe=False)

class GetUserStats(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BearerToken,)
    def get(self,request,*args,**kwargs):
        user = AppUser.objects.filter(user=request.user).first()
        content_object = s3.Object(AWS_STORAGE_BUCKET_NAME, f'processed/{user.stats_id}.json')
        file_content = content_object.get()['Body'].read().decode('utf-8')
        json_content = json.loads(file_content)
        return JsonResponse(data={"data":json_content}, safe=False)
