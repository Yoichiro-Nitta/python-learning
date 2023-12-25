from django.contrib import admin
from pythonL.models import IntroCourse, Basis, Quartet, Competition
from .models import CustomUser
# Register your models here.


class BasisAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'unit', 'section', "category", "q_key")

admin.site.register(IntroCourse)
admin.site.register(Basis, BasisAdmin) 
admin.site.register(Quartet)       
admin.site.register(Competition)
admin.site.register(CustomUser)