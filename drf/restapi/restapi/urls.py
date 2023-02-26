from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import PostViewSet, CommentViewSet, create_user
from django.contrib import admin
from django.urls import path


router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('users/create/', create_user, name='create_user'),
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
]