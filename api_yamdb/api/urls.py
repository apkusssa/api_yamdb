from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, GenreViewSet,
                    TitleViewSet, UserSignUpViewSet,
                    UserGetTokenViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'auth/signup', UserSignUpViewSet)
router.register(r'auth/token', UserGetTokenViewSet)
#router.register(r'users', UserRegistrationViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
]
