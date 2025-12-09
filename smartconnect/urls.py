from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from api.serializers import TokenOnlyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenOnlyView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),  # Para login en DRF UI
]

# Servir archivos estáticos en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
