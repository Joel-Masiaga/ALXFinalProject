from rest_framework import serializers
from blog.models import Category, Tag, Post
from users.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # display author details, set to read-only since it will be set automatically
    category = CategorySerializer(read_only=True)  # display category details
    tags = TagSerializer(many=True, read_only=True)  # display associated tags

    # Include fields for setting category and tags by their ID when creating or updating a post
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), source='tags', write_only=True
    )

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'created_at', 'updated_at',
            'author', 'category', 'tags', 'category_id', 'tag_ids'
        ]

    def create(self, validated_data):
        # Pop out nested fields category and tags
        category = validated_data.pop('category', None)
        tags = validated_data.pop('tags', [])
        
        # Create the post instance
        post = Post.objects.create(**validated_data)
        
        # Set category and tags
        if category:
            post.category = category
        if tags:
            post.tags.set(tags)

        post.save()
        return post

    def update(self, instance, validated_data):
        # Pop out nested fields category and tags
        category = validated_data.pop('category', None)
        tags = validated_data.pop('tags', None)

        # Update post instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Set category and tags
        if category:
            instance.category = category
        if tags is not None:
            instance.tags.set(tags)

        instance.save()
        return instance