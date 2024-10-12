from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import Http404
from blog.models import Post, Category, Tag
from .serializers import PostSerializer, CategorySerializer, TagSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters


# Custom permission class to check if the user is the owner of the object
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the author of the object
        return obj.author == request.user


# Custom filter for PostViewSet to filter by category and published date
class PostFilter(filters.FilterSet):
    # Optional filters for published date and category
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
    filterset_class = PostFilter  # Apply the custom filter class
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]  # Adding filtering, search, and ordering backends
    search_fields = ['title', 'content', 'tags__name', 'author__username']  # Fields for search functionality
    ordering_fields = ['created_at', 'title']  # Allow ordering by published date or title

    def perform_create(self, serializer):
        # Automatically set the author of the post to the current user
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Ensure the current user is the author of the post before updating
        if self.get_object().author != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this post.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Ensure the current user is the author of the post before deleting
        if instance.author != request.user:
            return Response({"detail": "You do not have permission to delete this post."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Custom action to retrieve posts by a specific author
    @action(detail=False, methods=['get'], url_path='author/(?P<author_id>\d+)', permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def posts_by_author(self, request, author_id=None):
        """
        Retrieve all posts by a specific author.
        """
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
    filter_backends = [DjangoFilterBackend, SearchFilter]  # Adding filtering and search backends
    search_fields = ['name']  # Fields for search functionality

    def perform_create(self, serializer):
        # Automatically set the author of the category to the current user
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Ensure the current user is the author of the category before updating
        if self.get_object().author != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this category.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Ensure the current user is the author of the category before deleting
        if instance.author != request.user:
            return Response({"detail": "You do not have permission to delete this category."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ViewSet for Tags
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]  # Adding filtering and search backends
    search_fields = ['name']  # Fields for search functionality

    def perform_create(self, serializer):
        # Automatically set the author of the tag to the current user
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        # Ensure the current user is the author of the tag before updating
        if self.get_object().author != self.request.user:
            raise permissions.PermissionDenied("You do not have permission to edit this tag.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Ensure the current user is the author of the tag before deleting
        if instance.author != request.user:
            return Response({"detail": "You do not have permission to delete this tag."}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


