from django.contrib import admin
from .models import TypeContent, Content, Creator, ReasonsToBuy, User


admin.site.register(TypeContent)
admin.site.register(Creator)
admin.site.register(ReasonsToBuy)
admin.site.register(Content)
admin.site.register(User)

