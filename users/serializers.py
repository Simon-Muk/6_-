from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer
)
from .models import ConfirmationCode
from .models import CustomUser
from users.models import CustomUser
from django.contrib.auth import authenticate


class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class AuthValidateSerializer(UserBaseSerializer):
    pass


class RegisterValidateSerializer(UserBaseSerializer):
    def validate_email(self, email):
        try:
            CustomUser.objects.get(email=email)
        except:
            return email
        raise ValidationError("User уже существует!")


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        code = attrs.get("code")

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("User не существует!")

        try:
            confirmation_code = ConfirmationCode.objects.get(user=user)
        except ConfirmationCode.DoesNotExist:
            raise ValidationError("Код подтверждения не найден!")

        if confirmation_code.code != code:
            raise ValidationError("Неверный код подтверждения!")

        return attrs


class RegisterSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = CustomUser

        fields = [
            'email',
            'password',
            'phone_number',
            'birthdate'
        ]

    def create(self, validated_data):

        password = validated_data.pop(
            'password'
        )

        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )

        return user
    

class LoginSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        email = attrs.get('email')

        password = attrs.get('password')

        user = authenticate(
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                'Invalid credentials'
            )

        attrs['user'] = user

        return attrs
    

class MyTokenObtainPairSerializer(
    TokenObtainPairSerializer
):

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)

        token['email'] = user.email

        token['birthdate'] = (
            str(user.birthdate)
            if user.birthdate
            else None
        )

        return token