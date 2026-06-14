from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from applications import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
