from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)


class UserManager(BaseUserManager):

    def create_user(
        self,
        email,
        password=None,
        **extra_fields
    ):

        if not email:
            raise ValueError(
                'Email is required'
            )

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields
    ):

        if not extra_fields.get(
            'phone_number'
        ):
            raise ValueError(
                'Superuser must have phone number'
            )

        extra_fields.setdefault(
            'is_staff',
            True
        )

        extra_fields.setdefault(
            'is_superuser',
            True
        )

        extra_fields.setdefault(
            'is_active',
            True
        )

        return self.create_user(
            email,
            password,
            **extra_fields
        )


class CustomUser(
    AbstractBaseUser,
    PermissionsMixin
):
    
    birthdate = models.DateField(
        null=True,
        blank=True
    )

    email = models.EmailField(
        unique=True
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        return self.email


class ConfirmationCode(models.Model):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='confirmation_code'
    )

    code = models.CharField(
        max_length=6
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'Код подтверждения для {self.user.email}'