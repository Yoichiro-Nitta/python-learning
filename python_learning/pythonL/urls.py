from django.urls import path
from .views import index
from .views import drill
from .views import compe

app_name = 'pythonL'
urlpatterns = [
    path('', index.top_page, name='index'),
    path('signup_view', index.signup_view, name='signup_view'),
    path('login_view', index.login_view, name='login_view'),
    path('login_req', index.login_req, name='login_req'),
    path('logout_view', index.logout_view, name='logout_view'),
    path('intro', index.intro, name='intro'),
    path('intro_ex/<int:pk>', index.intro_ex, name='intro_ex'),
    path('questions', index.questions, name='questions'),
    path('practice', drill.practice, name='practice'),
    path('practice_a', drill.practice_a, name='practice_a'),
    path('drill/<int:un>/<int:pk>', drill.drill, name='drill'),
    path('drill_a/<int:un>/<int:pk>', drill.drill_a, name='drill_a'),
    path('compe/<int:pk>', compe.compe, name='compe'),
    path('compe_a/<int:pk>', compe.compe_a, name='compe_a'),
]