### Что это за проект???
Это Django веб-сайт, который предоставляет информацию об играх, фильмах, сериалах и т.д. В нем реализована система рекомендаций, на основе глубокого обучения, опираясь на оценку самого контента предоставляемой админом(в основном берется средняя арифметическая с сайтов, которые оценивают) и контента который нравиться пользователю.

### Как выглядит веб-сайт на самом деле!
1) Главная страница сайта, где просто выгружается весь контент, без сортировок. Но на ней видеться поиск интересующего контента(поисковая строка в правом левом углу). В добавок если понравился контент можно пометить его, нажав на сердечко справа верхнем углу карточки контента(серая - если не нравиться, красная - нравиться).![Pasted image 20250617124525.png](https://github.com/Provod228/recommendations_project/blob/main/image_files/Pasted%20image%2020250617124525.png)
2) Страница рекомендаций, в ней обычно появляется контент который скорее всего придет по вкусу пользователя, в добавок, там не отображается контент который уже нравится пользователю, что увеличивает шансы найти интересующий пользователя контент. Если пользователь не авторизован, то система по умолчанию будет ставить контент который больше всего оценивается админом.![Pasted image 20250617130113.png](https://github.com/Provod228/recommendations_project/blob/main/image_files/Pasted%20image%2020250617130113.png)
3) Страница профиля пользователя, в ней отображается частичная информация о пользователе и контент, который ему нравится.![Pasted image 20250617130402.png](https://github.com/Provod228/recommendations_project/blob/main/image_files/Pasted%20image%2020250617130402.png)
4) На всех страницах можно было нажать на картинку карточки контента и узнать подробную информацию. Здесь можно узнать оценку контента, описание, создателей, причины попробовать, мелкие детали и так же добавить в избранное.![Pasted image 20250617130706.png](https://github.com/Provod228/recommendations_project/blob/main/image_files/Pasted%20image%2020250617130706.png)![Pasted image 20250617130717.png](https://github.com/Provod228/recommendations_project/blob/main/image_files/Pasted%20image%2020250617130717.png)
5) Так же можно выйти(серая дверь), зайти(светлая дверь) и зарегистрироваться на сайте, для того чтобы разблокировать более точный подбор контента для каждого пользователя.![Pasted image 20250617132331.png](https://github.com/Provod228/recommendations_project/blob/main/image_files/Pasted%20image%2020250617132331.png)![Pasted image 20250617132410.png](https://github.com/Provod228/recommendations_project/blob/main/image_files/Pasted%20image%2020250617132410.png)
### Как запустить проект.
1. Установите IDE(PyCharm может сам установить python) или python на ваше устройство.
2. Создайте папку и зайдите в папку с этой командой.
```
python -m venv namevenv
```
3. Активируйте виртуальное окружение.
```
cd namevenv\Scripts\activate
```
4. Установить все библиотеки python.
```
pip install -r requirements.txt
```
5. Запустите проект и переедите по ссылке.
```
cd .\metanit\
python manage.py runserver
```
### Детали самого проекта и код(сюда лесть можно только программистам).
#### Структура самого проекта
```
pythonProject4/                # Корень проекта
├── .venv/                     # Виртуальное окружение
├── metanit/                   # Основное приложение Django
│   ├── __init__.py
│   ├── settings.py            # Настройки проекта
│   ├── urls.py                # Главные URL-маршруты
│   ├── asgi.py                # ASGI-конфигурация
│   └── wsgi.py                # WSGI-конфигурация
├── application/               # Основное приложение
│   ├── migrations/            # Миграции базы данных
│   ├── static/                # Статические файлы
│   ├── templates/             # Шаблоны
│   │   ├── registration/      # Шаблоны аутентификации
│   │   │   ├── login.html
│   │   │   └── logged_out.html
│   │   └── (другие HTML-шаблоны)
│   ├── __init__.py
│   ├── admin.py               # Админ-панель
│   ├── apps.py                # Конфигурация приложения
│   ├── forms.py               # Формы
│   ├── models.py              # Модели данных
│   ├── recommendation_service.py  # Сервис рекомендаций
│   ├── serializers.py         # Сериализаторы
│   ├── urls.py                # URL-маршруты приложения
│   └── views.py               # Представления
├── media/                     # Загружаемые файлы
│   └── (пользовательские загрузки)
├── tests/                     # Тесты
│   └── test_metanit/          # Тесты приложения
│       ├── __init__.py
│       ├── conftest.py        # Фикстуры pytest
│       └── test_urls.py       # Тесты URL
├── requirements.txt           # Все зависимости проекта
├── db.sqlite3                 # База данных SQLite
└── manage.py                  # Управляющий скрипт
```
#### Более подробно о самих файлах в структуре
В этой части подробнее разберем код, а тесты будут разбираться позже. В этой части не будут разбираться: migrations(миграции моделей), static(css файлы), templates(html файлы), settings.py(тут мало настроек было, так что вдаваться в подробности не стоит), media(картинки контента) и другие менее важные файлы, которые генерируются при создании и ни как не изменяются. Потому что они интуитивно понятны и можете всегда посмотреть на самом github как они реализованы.
1) metanit/urls.py - в ней хранятся все url этого проекта и она объединяет все приложения проекта Django.
```
from django.contrib import admin  
from django.urls import path, include  
  
urlpatterns = [  
    path('admin/', admin.site.urls),  
    path('api-auth/', include('rest_framework.urls')),  
    path('', include('application.urls')),  
]
```
2) application/urls.py - все url приложения application.
```
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
```
3) views.py  - в ней хранятся все представления этого приложения, вот пример одного из них(самого важного в этом проекте).
```
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
            "recommended_content": serialized_content,  
            "liked_contents": list(liked_content_ids),  
            "user": request.user  
        })
```
4) serializers.py - реализованы простые сериализации
```
from rest_framework import serializers  
from .models import Content, TypeContent, Creator, ReasonsToBuy  
  
  
class TypeContentSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = TypeContent  
        fields = ["title_type"]  
  
  
class CreatorSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = Creator  
        fields = ["name", "summery"]  
  
  
class ReasonsToBuySerializer(serializers.ModelSerializer):  
    class Meta:  
        model = ReasonsToBuy  
        fields = ["summery"]  
  
  
class ContentSerializer(serializers.ModelSerializer):  
    creator = CreatorSerializer(many=True)  
    reasons_to_buy = ReasonsToBuySerializer(many=True)  
    type_content = TypeContentSerializer()  
  
    class Meta:  
        model = Content  
        fields = "__all__"
```
5) recommendation_service.py - сам алгоритм рекомендаций, основанный на глубоком обучении, сердце проекта.
```
import numpy as np  
import pandas as pd  
from sklearn.feature_extraction.text import TfidfVectorizer  
from sklearn.metrics.pairwise import cosine_similarity  
from tensorflow.keras.models import Model  
from tensorflow.keras.layers import Input, Embedding, Flatten, Dense, Concatenate  
from tensorflow.keras.optimizers import Adam  
from django.db.models import Count, Avg  
from .models import *  
  
  
class RecommendationEngine:  
    def __init__(self):  
        self.content_similarity_matrix = None  
        self.user_item_matrix = None  
        self.deep_model = None  
        self.content_features = None  
        self.user_features = None  
  
    def prepare_content_features(self):  
        # Собираем фичи для контента  
        contents = Content.objects.all().prefetch_related('creator', 'type_content', 'reasons_to_buy')  
  
        content_data = []  
        for content in contents:  
            creators = " ".join([c.name for c in content.creator.all()])  
            reasons = " ".join([r.summery for r in content.reasons_to_buy.all()])  
  
            content_data.append({  
                'id': content.id,  
                'title': content.title,  
                'summary': content.summery,  
                'type': content.type_content.title_type,  
                'creators': creators,  
                'reasons': reasons,  
                'evaluation': content.evaluation  
            })
			...
```
6) models.py - здесь хранятся все модели этого проекта
```
class Content(models.Model):  
    image = models.ImageField(  
        verbose_name="Картинка контента",  
        help_text="Вставте картинку контента",  
    )  
    title = models.CharField(  
        max_length=200,  
        verbose_name="Название контента",  
        help_text="Введите название контента",  
    )  
    summery = models.TextField(  
        max_length=1000,  
        verbose_name="Описание контента",  
        help_text="Введите описание контента",  
    )  
    creator = models.ManyToManyField(  
        Creator,  
        verbose_name="Создатель контента",  
        help_text="Введите создателя контента",  
    )  
    evaluation = models.FloatField(  
        verbose_name='Оценка',  
        validators=[  
            MinValueValidator(1.0, message='Оценка не может быть меньше 1.0'),  
            MaxValueValidator(10.0, message='Оценка не может быть больше 10.0')  
        ],  
        help_text='Оценка от 1.0 до 10.0'  
    )  
    created_at = models.DateTimeField(auto_now_add=True)  
    reasons_to_buy = models.ManyToManyField(  
        ReasonsToBuy,  
        verbose_name="Причины опробовать данный контент",  
        help_text="Введите причины опробовать данный контент",  
    )  
    type_content = models.ForeignKey(  
        TypeContent,  
        on_delete=models.CASCADE,  
        verbose_name="Типы контента",  
        help_text="Введите типы контента",  
    )  
  
    def __str__(self):  
        return self.title
```
7) forms.py - формы для заполнения чего либо, в данном случае есть только для регистрации пользователя.
```
from django.contrib.auth.forms import UserCreationForm  
from .models import User  
  
  
class SignUpUserForm(UserCreationForm):  
    class Meta:  
        model = User  
        fields = ('username', 'email')
```
#### Разбор тестов
В данном проекте используется библиотека pytest, как самая лучшая в своей стези.
1) conftest.py  - файл где хранятся фикстуры, которые используются много раз или же дублируются в разных файлах
```
import pytest  
from application.models import Content  
  
  
@pytest.fixture(scope='function')  
def test_url(request: None) -> str:  
    return 'http://127.0.0.1:8000/'  
  
  
@pytest.fixture(scope='function')  
def test_content_id(db) -> list:  
    return [str(content.id) for content in Content.objects.all()]
```
2) test_urls.py - тесты работающих url, которые тестируются при запуске самого сайта.
```
import pytest  
from application.models import Content  
  
  
@pytest.fixture(scope='function')  
def test_url(request: None) -> str:  
    return 'http://127.0.0.1:8000/'  
  
  
@pytest.fixture(scope='function')  
def test_content_id(db) -> list:  
    return [str(content.id) for content in Content.objects.all()]
```
3) test_views.py - тесты вьюшек.
```
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
```
