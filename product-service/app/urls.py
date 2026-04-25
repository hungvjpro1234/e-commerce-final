from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
