from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()

router.register('categories', views.CategoryViewSet)
router.register('genres', views.GenreViewSet)
router.register('titles', views.TitleViewSet)
router.register('users', views.UserViewSet)
router.register(r'titles/(?P<title_id>\d+)/reviews',
                views.ReviewViewSet, basename='review')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet, basename='comments'
)

urlpatterns = [
    path('v1/auth/signup/', views.EmailConfirmation.as_view()),
    path('v1/auth/token/', views.GetToken.as_view()),
    path('v1/', include(router.urls)),
]
