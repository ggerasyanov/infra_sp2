from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator

from reviews.models import Category, Comment, Genre, Review, Title, User


class UserConfirmationSerializer(serializers.ModelSerializer):
    """Сериализатор для view класса EmailConfirmation."""

    class Meta:
        fields = ('email', 'username')
        model = User

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя me в качестве username запрещено'
            )
        return value


class TokenSerializer(serializers.Serializer):
    """Сериализатор для view класса GetToken."""
    username = serializers.CharField(max_length=20)
    confirmation_code = serializers.CharField(max_length=30)

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        check_token = default_token_generator.check_token(
            user,
            data['confirmation_code']
        )
        if not check_token:
            raise serializers.ValidationError(
                'Неверный код подтверждения'
            )
        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('pub_date',)

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        author = self.context['request'].user
        title = get_object_or_404(
            Title, id=self.context['view'].kwargs.get('title_id')
        )
        if title.reviews.filter(author=author.id).exists():
            raise serializers.ValidationError(
                'Нельзя оставлять больше одного отзыва на произведение.'
            )
        return data

    def validate_score(self, value):
        if 1 <= value <= 10:
            return value
        raise serializers.ValidationError(
            'Оценка должна быть от 1 до 10.'
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User
        read_only_fields = ('role',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('pub_date', )
