from django.contrib import admin
from pythonL.models import IntroCourse, Basis, Quartet, Competition
from .models import CustomUser
# Register your models here.


admin.site.register(IntroCourse)
admin.site.register(Basis) 
admin.site.register(Quartet)       
admin.site.register(Competition)
admin.site.register(CustomUser)