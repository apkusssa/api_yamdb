from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    TitleViewSet, ReviewViewSet, UserRegistrationViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'auth/signup', UserRegistrationViewSet)
router.register(r'users', UserRegistrationViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

urlpatterns = [
    path('v1/', include(router.urls)),
]
