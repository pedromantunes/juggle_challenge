from __future__ import annotations

from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import routers, permissions
from rest_framework_simplejwt import views as jwt_views

from django.conf.urls import url

from . import views

router = routers.DefaultRouter()
router.register("users", views.CreateUserViewSet)
router.register("business", views.BusinessCreateViewSet)
router.register("business", views.BusinessRetrieveUpdateViewSet)
router.register("professionals", views.ProfessionalViewSet)
router.register("jobs", views.JobViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Juggle API",
        default_version="v1",
        description="Job Post",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("v1/", include(router.urls)),
    path("admin/", admin.site.urls),
    path(
        "v1/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "v1/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),
    url(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
