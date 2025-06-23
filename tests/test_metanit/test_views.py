import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from mixer.backend.django import mixer
from django.test import TestCase
from application.models import Content, User, TypeContent


@pytest.mark.django_db
class TestRecommendationsView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = mixer.blend(User)
        self.content = mixer.blend(Content)
        self.url = reverse('recommendations')

    def test_recommendations_view_works(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert 'recommended_content' in response.data
        assert 'liked_contents' in response.data
        assert 'user' in response.data

    def test_recommendations_unauthenticated(self):
        response = self.client.get(self.url)
        assert response.status_code == 200  # AllowAny permission


@pytest.mark.django_db
class TestUserRegistrationView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('signup')

    def test_registration_view_get(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert 'form' in response.data

    def test_registration_view_post_valid(self):
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        }
        response = self.client.post(self.url, data)
        assert response.status_code == 302  # Redirect after success
        assert User.objects.filter(username='testuser').exists()

    def test_registration_view_post_invalid(self):
        data = {
            'username': '',
            'email': 'invalid',
            'password1': '123',
            'password2': '456'
        }
        response = self.client.post(self.url, data)
        assert response.status_code == 200  # Stays on page with errors
        assert 'form' in response.data


@pytest.mark.django_db
class TestProfileUserView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = mixer.blend(User)
        self.content = mixer.blend(Content)
        self.user.content_like.add(self.content)
        self.url = reverse('profile')

    def test_profile_view_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert 'profile' in response.data
        assert 'content' in response.data
        assert 'liked_contents' in response.data
        assert len(response.data['liked_contents']) == 1

    def test_profile_view_unauthenticated(self):
        response = self.client.get(self.url)
        assert response.status_code == 403  # IsAuthenticated permission


@pytest.mark.django_db
class TestContentDetailView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.content = mixer.blend(Content)
        self.url = reverse('content-detail', kwargs={'id': self.content.id})

    def test_content_detail_view_works(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert 'content' in response.data
        assert 'liked_contents' in response.data

    def test_content_detail_with_likes(self):
        user = mixer.blend(User)
        user.content_like.add(self.content)
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert self.content.id in response.data['liked_contents']


@pytest.mark.django_db
class TestContentListView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('content-list')
        self.type_content = mixer.blend(TypeContent)
        self.content1 = mixer.blend(Content, type_content=self.type_content)
        self.content2 = mixer.blend(Content, type_content=self.type_content)

    def test_content_list_view_works(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert len(response.data['content']) == 2
        assert 'liked_contents' in response.data
        assert 'type_content_choices' in response.data

    def test_content_list_filtering(self):
        response = self.client.get(
            self.url,
            {'type_content': [self.type_content.title_type]}
        )
        assert response.status_code == 200
        assert len(response.data['content']) == 2

    def test_content_list_search(self):
        response = self.client.get(
            self.url,
            {'search': self.content1.title[:3]}
        )
        assert response.status_code == 200
        assert len(response.data['content']) >= 1

    def test_content_list_ordering(self):
        response = self.client.get(
            self.url,
            {'ordering': '-created_at'}
        )
        assert response.status_code == 200
        dates = [item['created_at'] for item in response.data['content']]
        assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
class TestContentLikeAction(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = mixer.blend(User)
        self.content = mixer.blend(Content)
        self.url = reverse('content-like', kwargs={'content_id': self.content.id})

    def test_like_action_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        assert response.status_code == 302  # Redirect
        assert self.content in self.user.content_like.all()

    def test_unlike_action(self):
        self.user.content_like.add(self.content)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        assert response.status_code == 302
        assert self.content not in self.user.content_like.all()

    def test_like_action_unauthenticated(self):
        response = self.client.post(self.url)
        assert response.status_code == 403