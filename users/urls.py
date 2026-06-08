from django.urls import path
from users.views import RegistrationAPIView, AuthorizationAPIView, ConfirmUserAPIView, MyTokenObtainPairView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

urlpatterns = [
    path('registration/', RegistrationAPIView.as_view()),
    path('authorization/', AuthorizationAPIView.as_view()),
    path('confirm/', ConfirmUserAPIView.as_view()),
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),

    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            url_name='schema'
        ),
        name='swagger-ui'
    ),

    path(
        'api/tokem/',
        MyTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'google/login/',
        GoogleLoginAPIView.as_view()
    ),

    path(
        'google/callback/',
        GoogleCallbackAPIView.as_view()
    ),
]