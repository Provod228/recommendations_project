from django.contrib import admin
from django.urls import path, include
from .views import ContentListView, RecommendationsView, UserRegistrationView, ProfileUserView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('content/', ContentListView.as_view(), name='content-list'),
    path('content/<int:content_id>/like/', ContentListView.as_view(), name='content-like'),
    path('recommendations/', RecommendationsView.as_view(), name='recommendations'),
    path('accounts/signup/', UserRegistrationView.as_view(), name='signup'),
    path('profile/', ProfileUserView.as_view(), name="profile"),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)