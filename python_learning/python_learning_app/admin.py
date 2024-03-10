from django.contrib import admin
from python_learning_app.models.index import CustomUser,  News
from python_learning_app.models.questions import IntroCourse, Basis, Quartet,QuartetResult, Competition, CompeResult
from .models import CustomUser
# Register your models here.


class IntroCourseAdmin(admin.ModelAdmin):
    ordering = ("section", "order")

class BasisAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'unit', 'section', "category", "q_key")
    ordering = ("primary_key", )

class QuartetAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'frame')
    ordering = ("primary_key", )

class CompetitionAdmin(admin.ModelAdmin):
    ordering = ("primary_key", )

admin.site.register(IntroCourse, IntroCourseAdmin)
admin.site.register(Basis, BasisAdmin) 
admin.site.register(Quartet, QuartetAdmin)
admin.site.register(QuartetResult)            
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(CompeResult)
admin.site.register(CustomUser)
admin.site.register(News)