import os
import random
import string

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView
)

from users.models import CustomUser
from users.tasks import send_welcome_message
from users.tasks import send_confirmation_email

from common.redis import redis_client

from .serializers import (
    AuthValidateSerializer,
    ConfirmationSerializer,
    RegisterValidateSerializer,
    MyTokenObtainPairSerializer,
)


class AuthorizationAPIView(APIView):
    def post(self, request):
        serializer = AuthValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(**serializer.validated_data)

        if user:
            if not user.is_active:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={"error": "User account is not activated yet!"},
                )

            token, _ = Token.objects.get_or_create(user=user)
            return Response(data={"key": token.key})

        return Response(
            status=status.HTTP_401_UNAUTHORIZED,
            data={"error": "User credentials are wrong!"},
        )


class RegistrationAPIView(CreateAPIView):
    serializer_class = RegisterValidateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Use transaction to ensure data consistency
        with transaction.atomic():
            user = CustomUser.objects.create_user(
                email=email, password=password, is_active=False
            )

            # Create a random 6-digit code
            code = "".join(random.choices(string.digits, k=6))

            redis_client.set(
                f'confirmation_code:{user.email}',
                code,
                ex=300
)


        return Response(
            status=status.HTTP_201_CREATED,
            data={"user_id": user.id, "confirmation_code": code},
        )


class ConfirmUserAPIView(APIView):
    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = serializer.validated_data["user_id"]
        send_welcome_message.delay(user.email)
        send_confirmation_email.delay(
            user.email,
            code
        )

        with transaction.atomic():
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

            token, _ = Token.objects.get_or_create(user=user)


        return Response(
            status=status.HTTP_200_OK,
            data={"message": "User аккаунт успешно активирован", "key": token.key},
        )


class MyTokenObtainPairView(
    TokenObtainPairView
):

    serializer_class = (
        MyTokenObtainPairSerializer
    )


class GoogleLoginAPIView(APIView):

    def get(self, request):

        client_id = os.getenv(
            'GOOGLE_CLIENT_ID'
        )

        redirect_uri = (
            'http://127.0.0.1:8000'
            '/api/v1/users/google/callback/'
        )

        google_auth_url = (
            'https://accounts.google.com/o/oauth2/v2/auth'
            f'?client_id={client_id}'
            f'&redirect_uri={redirect_uri}'
            '&response_type=code'
            '&scope=openid email profile'
        )

        return Response({
            'auth_url': google_auth_url
        })
    

class GoogleCallbackAPIView(APIView):

    def get(self, request):
        return Response({
            'message': 'Google callback works'
        })