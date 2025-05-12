from django.contrib import admin
from django.urls import path, include
from .views import TestView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("test/", TestView.as_view(), name="test_data")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
