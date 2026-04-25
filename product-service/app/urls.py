from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, InternalProductViewSet, ProductViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")
router.register("internal/products", InternalProductViewSet, basename="internal-product")

urlpatterns = router.urls
