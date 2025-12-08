"""
URL configuration for draccs_be project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # API endpoints
    path("api/", include("backend_app.accounts.urls")),            # /api/accounts/...
    path("api/", include("backend_app.drone_registration.urls")),  # /api/drone_registration/...
    path("api/", include("backend_app.orderform.urls")),           # /api/orders/, /api/order-delivery-info/...
    path("api/", include("backend_app.client.urls")),
    path("api/", include("backend_app.drone_image.urls")),
]

# Serve uploaded files (like PDFs) in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)