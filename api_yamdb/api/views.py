from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, User

from . import permissions, serializers
from .filters import TitleFilter
from api_yamdb.settings import EMAIL


class EmailConfirmation(APIView):
    """Отправка кода подтверждения на email, переданный в запросе."""
    def post(self, request):
        email = request.data.get('email')
        serializer = serializers.UserConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(email=email)
        confirmation_code_gen = PasswordResetTokenGenerator()
        confirmation_code = confirmation_code_gen.make_token(user)
        send_mail(
            'Код подтверждения',
            confirmation_code,
            EMAIL,
            [email],
            fail_silently=False,
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class GetToken(APIView):
    "Создание JWT токена."
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'token': str(refresh.access_token),
        }

    def post(self, request):
        serializer = serializers.TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(username=request.data.get('username'))
        return Response(self.get_tokens_for_user(user),
                        status=status.HTTP_200_OK)


class CategoryAndGenreViewSet(mixins.CreateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    permission_classes = [permissions.IsSuperuserOrReadOnly]
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name',)


class CategoryViewSet(CategoryAndGenreViewSet):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer


class GenreViewSet(CategoryAndGenreViewSet):
    queryset = Genre.objects.all()
    serializer_class = serializers.GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = serializers.TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [permissions.IsSuperuserOrReadOnly | IsAdminUser]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return serializers.TitleWriteSerializer
        return serializers.TitleSerializer


class ReviewAndCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AuthorAdminOrReadOnly, )
    pagination_class = LimitOffsetPagination


class ReviewViewSet(ReviewAndCommentViewSet):
    """Всьюстер для модели Review."""
    serializer_class = serializers.ReviewSerializer

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(title=title, author=self.request.user)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.reviews.all()


class CommentViewSet(ReviewAndCommentViewSet):
    """Всьюстер для модели Comment."""
    serializer_class = serializers.CommentSerializer

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(review=review, author=self.request.user)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review.comments.all()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'
    permission_classes = (permissions.IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)

    @action(
        methods=['get', 'patch'], detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, pk=None):
        if request.method == 'GET':
            serializer = self.get_serializer(instance=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.user.is_user:
            serializer = serializers.UserRoleSerializer(
                instance=request.user, data=request.data, partial=True
            )
        else:
            serializer = self.get_serializer(
                instance=request.user, data=request.data, partial=True
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
