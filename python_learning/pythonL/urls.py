from django.urls import path
from . import views

app_name = 'pythonL'
urlpatterns = [
    path('', views.top_page, name='index'),
    path('signup_view', views.signup_view, name='signup_view'),
    path('login_view', views.login_view, name='login_view'),
    path('login_req', views.login_req, name='login_req'),
    path('logout_view', views.logout_view, name='logout_view'),
    path('intro', views.intro, name='intro'),
    path('intro_ex/<int:pk>', views.intro_ex, name='intro_ex'),
    path('questions', views.questions, name='questions'),
    path('practice', views.practice, name='practice'),
    path('practice_a', views.practice_a, name='practice_a'),
    path('drill/<int:un>/<int:pk>', views.drill, name='drill'),
    path('drill_a/<int:un>/<int:pk>', views.drill_a, name='drill_a'),
]