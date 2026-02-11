from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.auth import AdminTokenObtainPairView
from api.viewsets import RideEventViewSet, RideViewSet, UserViewSet
from api.views import health

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"rides", RideViewSet, basename="ride")
router.register(r"ride-events", RideEventViewSet, basename="ride-event")

urlpatterns = [
    path("health/", health, name="health"),
    path("auth/token/", AdminTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns += router.urls
