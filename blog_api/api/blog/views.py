from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import Http404
from blog.models import Post, Category, Tag
from .serializers import PostSerializer, CategorySerializer, TagSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters


# Customized permission class - this checks if the user is the owner of the post
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request\any user
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the author of the post
        return obj.author == request.user


# Custom Filter for PostViewSet to filter by category and published date
class PostFilter(filters.FilterSet):
    # filters for published date and category
    start_date = filters.DateFilter(field_name="created_at", lookup_expr="gte")
    end_date = filters.DateFilter(field_name="created_at", lookup_expr="lte")
    category = filters.CharFilter(field_name="category__name")

    class Meta:
        model = Post
        fields = ['category', 'tags', 'author', 'created_at']


# ViewSet for Posts
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filterset_class = PostFilter  # custom filter class
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]  
    search_fields = ['title', 'content', 'tags__name', 'author__username']  
    ordering_fields = ['created_at', 'title'] 

    def perform_create(self, serializer):
        # automatically set the author of the post to the current user
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # ensure that the current user is the author of the post before updating
        if self.get_object().author != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this post!")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # ensure that the current user is the author of the post before deleting
        if instance.author != request.user:
            return Response({"detail": "You do not have permission to delete this post!"}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Retrieve posts by a specific author
    @action(detail=False, methods=['get'], url_path='author/(?P<author_id>\d+)', permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def posts_by_author(self, request, author_id=None):
        posts = Post.objects.filter(author=author_id)
        if not posts:
            return Response({"detail": "No posts found for this author."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ViewSet for Categories
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]  
    search_fields = ['name']  

    def perform_create(self, serializer):
        # automatically set the author of the category to the current user
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # ensure that the current user is the author of the category before updating
        if self.get_object().author != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this category!")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # ensure that the current user is the author of the category before deleting
        if instance.author != request.user:
            return Response({"detail": "You do not have permission to delete this category!"}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ViewSet for Tags
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter] 
    search_fields = ['name']  

    def perform_create(self, serializer):
        # automatically set the author of the tag to the current user
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # ensure that the current user is the author of the tag before updating
        if self.get_object().author != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this tag!")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # ensure that the current user is the author of the tag before deleting
        if instance.author != request.user:
            return Response({"detail": "You do not have permission to delete this tag!"}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


