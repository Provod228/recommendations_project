from django.db.models import Q
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, MultipleChoiceFilter
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Content
from .serializers import ContentSerializer
from django.shortcuts import render, get_object_or_404
from .recommendation_service import RecommendationEngine
from django.shortcuts import redirect
from .forms import SignUpUserForm
from .models import User, TypeContent
from rest_framework import permissions, status


recommendation_engine = RecommendationEngine()


class RecommendationsView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'recommendations.html'
    permission_classes = [permissions.AllowAny]

    def get(self, request) -> Response:
        try:
            user = request.user
            liked_content = user.content_like.all()
            liked_content_ids = {content.id for content in liked_content}
        except Exception as e:
            liked_content_ids = set()

        try:
            recommendation_engine.prepare_content_features()
            recommendation_engine.prepare_user_item_matrix()
            recommendation_engine.train_deep_model(epochs=5)
        except Exception as e:
            print(f"Error training model: {e}")
            recommended_content = recommendation_engine.get_popular_content()
        else:
            recommended_content = recommendation_engine.recommend_for_user(request.user.id)

        filtered_recommended = [
            item for item in recommended_content
            if item.id not in liked_content_ids
        ]

        # Сериализуем контент, чтобы creator был доступен в шаблоне
        serialized_content = ContentSerializer(filtered_recommended, many=True).data

        return Response({
            "recommended_content": serialized_content,  # Используем сериализованные данные
            "liked_contents": list(liked_content_ids),
            "user": request.user
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

        # Получаем только контент, который лайкнул пользователь
        liked_content = user.content_like.all()
        liked_contents_ids = list(liked_content.values_list('id', flat=True))

        context = {
            "profile": profile,
            "content": ContentSerializer(liked_content, many=True).data,  # Сериализуем лайкнутый контент
            "liked_contents": liked_contents_ids,  # Список ID лайкнутых элементов
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


class ContentDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'content_detail.html'
    permission_classes = [permissions.AllowAny]

    def get(self, request: None, id: int) -> Response:
        content = Content.objects.get(pk=id)
        return Response({
            'content': content,
                         })


class ContentFilter(FilterSet):
    type_content = MultipleChoiceFilter(
        field_name='type_content__title_type',
        lookup_expr='iexact',
        label='Тип контента'
    )

    search = CharFilter(method='custom_search', label='Поиск')

    class Meta:
        model = Content
        fields = []

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(summery__icontains=value) |
            Q(type_content__title_type__icontains=value) |
            Q(creator__name__icontains=value)
        )


class ContentListView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'main.html'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ContentFilter
    ordering_fields = ['title', 'evaluation', 'created_at']  # Убедитесь, что это поле существует в модели
    ordering = '-created_at'  # Сортировка по умолчанию

    def get_queryset(self):
        return Content.objects.all().distinct()

    def get_type_content_choices(self):
        return [(t.title_type, t.title_type) for t in TypeContent.objects.all()]

    def get(self, request):
        queryset = self.get_queryset()

        # Применяем фильтры
        content_filter = ContentFilter(request.GET, queryset=queryset)
        filtered_queryset = content_filter.qs

        # Применяем сортировку
        ordering = request.GET.get('ordering', self.ordering)
        if ordering:
            filtered_queryset = filtered_queryset.order_by(ordering)

        liked_contents = []
        if request.user.is_authenticated:
            liked_contents = request.user.content_like.values_list('id', flat=True)

        context = {
            "content": ContentSerializer(filtered_queryset, many=True).data,
            "liked_contents": list(liked_contents),
            "user": request.user,
            "search_query": request.GET.get('search', ''),
            "current_ordering": ordering,
            "type_content_choices": self.get_type_content_choices(),
            "selected_types": request.GET.getlist('type_content', []),
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

