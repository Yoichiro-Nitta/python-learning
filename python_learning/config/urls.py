"""
URL configuration for python_learning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

# 本番環境でエラー表示する場合は以下をuncomment
"""
from python_learning_app.views import index
handler500 = index.my_customized_server_error
"""


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('python_learning_app.urls')),
]
