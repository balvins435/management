"""Routes for category and resource endpoints."""

from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ResourceViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('resources', ResourceViewSet, basename='resource')

urlpatterns = router.urls
