from django.urls import path, include
from .views import ContentListView, RecommendationsView, UserRegistrationView, ProfileUserView, ContentDetailView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', ContentListView.as_view(), name='content-list'),
    path('content/', ContentListView.as_view(), name='content-list'),
    path('content/<int:id>', ContentDetailView.as_view(), name='content-detail'),
    path('content/<int:content_id>/like/', ContentListView.as_view(), name='content-like'),
    path('recommendations/', RecommendationsView.as_view(), name='recommendations'),
    path('accounts/signup/', UserRegistrationView.as_view(), name='signup'),
    path('profile/', ProfileUserView.as_view(), name="profile"),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)