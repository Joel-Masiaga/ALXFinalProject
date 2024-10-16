from rest_framework.routers import DefaultRouter
from api.blog.views import PostViewSet, CategoryViewSet, TagViewSet
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include

# creating a router
router = DefaultRouter()

# registering the viewsets with their respective base paths and viewset classes
router.register(r'posts', PostViewSet, basename='post')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')

# automatically generate URL patterns by the router and append login path
urlpatterns = [
    path('api/token/login/', obtain_auth_token),  # DRF token login
    path('', include(router.urls)),  # router-generated URLs
]
