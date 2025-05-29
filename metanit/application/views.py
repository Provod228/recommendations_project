from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Content
from .serializers import ContentSerializer
from django.shortcuts import render, get_object_or_404
from .recommendation_service import RecommendationEngine
from django.shortcuts import redirect
from .forms import SignUpUserForm
from .models import User, UserInteraction
from rest_framework import permissions, status



recommendation_engine = RecommendationEngine()


class ContentListView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'main.html'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        content = Content.objects.all()
        liked_contents = []
        if request.user.is_authenticated:
            liked_contents = request.user.content_like.values_list('id', flat=True)

        context = {
            "content": ContentSerializer(content, many=True).data,
            "liked_contents": list(liked_contents),
            "user": request.user
        }
        return Response(context)

    def post(self, request, content_id=None):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_403_FORBIDDEN
            )

        content = get_object_or_404(Content, id=content_id)

        if content in request.user.content_like.all():
            request.user.content_like.remove(content)
            liked = False
        else:
            request.user.content_like.add(content)
            liked = True

        # Для AJAX-запросов возвращаем JSON
        if request.accepted_renderer.format == 'json':
            return Response({
                "liked": liked,
                "count": content.liked_by.count(),
                "content_id": content_id
            })

        # Для обычных запросов перенаправляем обратно
        return redirect(request.META.get('HTTP_REFERER', 'content-list'))


class RecommendationsView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'recommendations.html'
    permission_classes = [permissions.AllowAny]

    def get(self, request) -> Response:
        try:
            user = request.user
            liked_content = user.content_like.all()
            liked_content_ids = {content.id for content in liked_content}  # Собираем ID лайкнутых элементов
        except Exception as e:
            liked_content_ids = set()  # Если ошибка — считаем, что лайков нет

        try:
            recommendation_engine.prepare_content_features()
            recommendation_engine.prepare_user_item_matrix()
            recommendation_engine.train_deep_model(epochs=5)
        except Exception as e:
            print(f"Error training model: {e}")
            recommended_content = recommendation_engine.get_popular_content()
        else:
            recommended_content = recommendation_engine.recommend_for_user(request.user.id)

        # Фильтруем recommended_content, убирая лайкнутые элементы
        filtered_recommended = [
            item for item in recommended_content
            if item.id not in liked_content_ids  # Предполагаем, что item имеет поле `id`
        ]

        return Response({
            "recommended_content": filtered_recommended,
        })


class UserRegistrationView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'signup.html'
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        form = SignUpUserForm()
        return Response({'form': form})

    def post(self, request) -> Response:
        form = SignUpUserForm(request.data)
        if form.is_valid():
            form.save()
            return redirect("login")
        else:
            return Response({'form': form})


class ProfileUserView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'profile.html'
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = get_object_or_404(User, pk=user.pk)

        liked_content = user.content_like.all()
        return Response({"profile": profile, "liked_content": ContentSerializer(liked_content, many=True).data})


class ContentLikedCardView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'profile.html'
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content = get_object_or_404(Content, id=request.content_id)
        print(content)
        if content in request.user.content_like.all():
            request.user.content_like.remove(content)
            liked = False
        else:
            request.user.content_like.add(content)
            liked = True
        return 0