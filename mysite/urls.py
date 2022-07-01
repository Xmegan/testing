from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blogs.urls')),
    path('blogs/', include('blogs.urls')),
    path('', include("django.contrib.auth.urls")),
]
