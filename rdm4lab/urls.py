"""
URL configuration for rdm4lab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.apps import apps

urlpatterns = [
    path("admin/", admin.site.urls),  # Admin site
    path("", include("main.urls")),  # Main app
    path("", include("django.contrib.auth.urls")),  # Authentication
    path("ckeditor/", include("ckeditor_uploader.urls")),  # CKEditor file uploader
]

# Include the URLs of the apps that are installed
EXPERIMENTS_APPS = ["G1", "G3"]
for app_name in EXPERIMENTS_APPS:
    # Check if the app with the given name is installed
    if apps.is_installed(app_name):
        # Include the URLs of the app with a unique namespace
        urlpatterns += [
            path(
                f"my-experiments/{app_name}/data~/",
                include(f"{app_name}.urls", namespace=app_name),
            )
        ]
    else:
        pass

# Add media files to urlpatterns only if DEBUG is True i.e. during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
