import os
import requests

from django.utils.timezone import now

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser


class GoogleCallbackAPIView(APIView):

    def get(self, request):

        code = request.GET.get('code')

        token_url = (
            'https://oauth2.googleapis.com/token'
        )

        data = {
            'code': code,
            'client_id': os.getenv(
                'GOOGLE_CLIENT_ID'
            ),
            'client_secret': os.getenv(
                'GOOGLE_CLIENT_SECRET'
            ),
            'redirect_uri':
            'http://127.0.0.1:8000/api/v1/users/google/callback/',
            'grant_type': 'authorization_code'
        }

        token_response = requests.post(
            token_url,
            data=data
        )

        token_json = token_response.json()

        access_token = token_json.get(
            'access_token'
        )

        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={
                'Authorization':
                f'Bearer {access_token}'
            }
        )

        user_data = user_info_response.json()

        email = user_data.get('email')

        user, created = (
            CustomUser.objects.get_or_create(
                email=email
            )
        )

        user.first_name = user_data.get(
            'given_name',
            ''
        )

        user.last_name = user_data.get(
            'family_name',
            ''
        )

        user.is_active = True

        user.last_login = now()

        user.registration_source = 'google'

        user.save()

        refresh = RefreshToken.for_user(
            user
        )

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })