### Про что проект

Это веб-сайт, сделанный на фреймворке Django, служащий для добавление/ хранение / удаление учебных материалов. Только зарегистрированные пользователи могут скачивать/удалять и использовать данные материалы.

  

### Что по коду

В самом проекте хранится два основных файла: "jornal" и "WebJornal". И ещё есть третий файл, который хранит уже сами учебные материалы. В "Jornal" хранится основная логика всего проекта, его визуальная часть, бизнес-логика и работа с БД. В файле  "WebJornal" хранятся основные настройки Django и все URL-ссылки, включая ссылки на администрирование сайта.
1. jornal
	1. admin.py - идёт регистрация моделей, для будущей работы админа над проектом.
	```
	@admin.register(EducationalMaterial)  
	class EducationalMaterialAdmin(admin.ModelAdmin):  
	    list_display = ('title', 'subject')  
	    list_filter = ('subject',)
	```
	2. forms.py - создаёт поля для регистрации пользователя, добавление и сохранение нового учебного материала.
```
class EducationalMaterialForm(forms.ModelForm):  
    class Meta:  
        model = EducationalMaterial  
        fields = ('title', 'summary', 'material_file', 'subject')  
  
    def save(self, commit=True):  
        instance = super().save(commit=False)  
        if instance.material_file:  
            instance.material_file.name = f"material_{instance.title}_{instance.material_file.name}"  
        if commit:  
            instance.save()  
        return instance
```
	4. models.py - создание сущностей для миграции в БД и последующее использования сущностей как моделей в проекте.
```
class EducationalMaterial(models.Model):  
    title = models.CharField(  
        max_length=100,  
        help_text="Введите название предмет",  
        verbose_name="Название предмет",  
        null=False,  
    )  
    summary = models.TextField(  
        max_length=1000,  
        help_text='Введите краткое описание учебного материала',  
        verbose_name='Учебный материал',  
        null=False,  
    )  
    material_file = models.FileField(  
        help_text='Загрузите файл с учебным материалом',  
        verbose_name='Файл с учебным материалом',  
        null=False,  
        upload_to='material_files'  
    )  
    subject = models.ForeignKey(  
        'Subject', on_delete=models.CASCADE,  
        help_text='Выберите учебны предмет',  
        verbose_name='Учебны предмет', null=True,  
    )  
  
    def __str__(self):  
        return self.title
```
	5. serializers.py - позволяет конвертировать наборы запросов и экземпляры моделей в собственные типы данных, к примеру учебный материал(легко преобразовать в JSON, XML или другие типы контента).
```
class EducationalMaterialSerializer(serializers.ModelSerializer):  
    subject = serializers.CharField()  
  
    class Meta:  
        model = EducationalMaterial  
        fields = ('id', 'title', 'summary', 'material_file', 'subject')
```
	6. urls.py - создание собственных ссылок.
```
app_name = 'jornal'  
  
urlpatterns = [  
    path('signup/', UserRegistrationView.as_view(), name='signup'),  
    path('main_page/', MainPageView.as_view(), name='main-page'),  
    path('main_page/add_educational_material', EducationalMaterialAddView.as_view(), name='educational_material_add'),  
    path('main_page/download/<int:material_id>/', download_material, name='download_material'),  
    path('delete/<int:material_id>/', EducationalMaterialDeleteView.as_view(), name='delete_educational_material'),  
    path('accounts/', include('django.contrib.auth.urls')),  
]
```
	7. views.py - создание API
```
class UserRegistrationView(APIView):  
    renderer_classes = [TemplateHTMLRenderer]  
    template_name = 'registration.html'  
  
    def get(self, request):  
        form = SignUpForm()  
        return Response({'form': form})  
  
    def post(self, request) -> Response:  
        form = SignUpForm(request.data)  
        if form.is_valid():  
            user = form.save()  
            login(request, user)  
            return redirect(reverse('jornal:main-page'))  
        else:  
            return Response({'form': form})
```
	8. templates - хранит в себе шаблоны страниц в формате html
	9. static - хранит стили css(CSS файл) для html и картинки(image файл)
	10. migrations - файл с миграциями моделей django
2. WebJornal
	1. settings.py - настройки django
	2. urls.py - собирает и создаёт все ссылки со всего проекта.
```
urlpatterns = [  
    path('jornal/', include('jornal.urls')),  
    path('admin/', admin.site.urls),  
]
```
	3. school.sqlite3 - База данных проекта.
3. material_files - файл хранит весь учебный материал
	  

### Функционал

При запуске основного сайта, мы переходим на главную страницу по ссылке  "jornal/main_page" . На данной стране мы видим учебный материал, который можно скачать, удалить или добавить, но только при одном условие, если вы вошли успешно авторизовались. В зависимости от аутентификации, у пользователя будет две кнопки: "войти" или "выйти". При нажатии на копку "войти" пользователь переходит на страницу входа, если пользователь отсутствует, то он может нажать кнопку "регистрация" и наоборот.

При нажатии кнопки "добавление материала" будет дана форма, по которой добавляется учебный материал.

### Запуск проекта на вашем устройстве
3. Скачать IDE (если вы не слабак)
4. Скачать Python версии не менее 3.12
5. Установить виртуальное окружение и активировать его
```
    python3 -m venv .venv
```
6. После установки .venv, переходим /Scripts/Activate
7. Клонировать с проект с github
```

    git clone "ссылка на проект"
```
8. Установить все библиотеки

```
    pip install -r requirements
```
9. Перейти в основной проект и написать в консоль команду запуска

```
    python manage.py runserver  
```

### Ручное тестирование
1. Сайт исправно работает и запускается сразу
	1. ![[Pasted image 20250210084542.png]]
	2. ![[Pasted image 20250210084654.png]]
2. Пользователь может зарегистрироваться и войти в систему с проверкой почты на валидность и хешируемым паролем
	1. ![[Pasted image 20250210084755.png]]
	2. ![[Pasted image 20250210084814.png]]
	3. ![[Pasted image 20250210084830.png]]
3. Есть доступ к скачиванию файлов и удалению
	1. ![[Pasted image 20250210084940.png]]
	2. ![[Pasted image 20250210085012.png]]
4. Работает добавление нового учебного материала
	1. ![[Pasted image 20250210085123.png]]
	2. ![[Pasted image 20250210085132.png]]
