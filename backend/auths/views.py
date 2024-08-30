from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import TokenSerializer, UserSerializer
from django.contrib.auth.models import User
from .models import VerificationCode
from django.core.mail import send_mail
from django.conf import settings
import requests

# Create your views here.
class GoogleLogin(GenericAPIView):
    def get(self, request):
        access_token = request.query_params.get('access_token')
        resp = requests.get(f"https://www.googleapis.com/oauth2/v2/userinfo", headers={
            "Authorization": f"Bearer {access_token}"
        }).json()
        user = User.objects.filter(email=resp['email'])
        if user:
            refresh = RefreshToken.for_user(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            serializer = TokenSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            json = JSONRenderer().render(serializer.data)
            return HttpResponse(json, status=200)
        else:
            data = {
                'email': resp['email'],
                'first_name': resp['given_name'],
                'last_name': resp['family_name']
            }
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            json = JSONRenderer().render(serializer.data)
            return HttpResponse(json, status=200)
        
         
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        last_name = request.data.get('last_name')
        first_name = request.data.get('first_name')
        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name)
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        serializer = TokenSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        json = JSONRenderer().render(serializer.data)
        return HttpResponse(json, status=200)
