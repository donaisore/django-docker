from rest_framework.routers import DefaultRouter

from blogs.views import BlogViewSet

router = DefaultRouter(trailing_slash=False)

router.register(
    r'^blogs',
    BlogViewSet,
    basename='blogs'
)

urlpatterns = router.urls
