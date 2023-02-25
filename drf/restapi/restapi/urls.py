from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import PostViewSet, CommentViewSet
from django.contrib import admin
from django.urls import path


router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
]