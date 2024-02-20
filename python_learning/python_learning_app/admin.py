from django.contrib import admin
from python_learning_app.models.index import CustomUser, IntroCourse, News
from python_learning_app.models.questions import Basis, Quartet, Competition, CompeResult
from .models import CustomUser
# Register your models here.


class BasisAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'unit', 'section', "category", "q_key")

admin.site.register(IntroCourse)
admin.site.register(Basis, BasisAdmin) 
admin.site.register(Quartet)       
admin.site.register(Competition)
admin.site.register(CompeResult)
admin.site.register(CustomUser)
admin.site.register(News)