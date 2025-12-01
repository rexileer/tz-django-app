from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from treemenu.api_views import MenuItemViewSet

# DRF Router для API
router = DefaultRouter()
router.register(r'menu', MenuItemViewSet, basename='menu')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # DRF API endpoints
    path('', include('treemenu.urls')),
]
