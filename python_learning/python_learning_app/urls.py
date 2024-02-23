from django.urls import path
from .views import index, drill, compe, quartet, machine
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

app_name = 'python_learning'
urlpatterns = [
    path('', index.top_page, name='index'),
    path('news_list', index.news_list, name='news_list'),
    path('signup_view', index.signup_view, name='signup_view'),
    path('login_view', index.login_view, name='login_view'),
    path('login_req', index.login_req, name='login_req'),
    path('logout_view', index.logout_view, name='logout_view'),
    path('intro', index.intro, name='intro'),
    path('intro_ex/<int:pk>', index.intro_ex, name='intro_ex'),
    path('questions', drill.questions, name='questions'),
    path('practice', drill.practice, name='practice'),
    path('practice_a', drill.practice_a, name='practice_a'),
    path('drill_beginner/<int:un>/<int:pk>', drill.DrillBeginner.as_view(), name='drill_beginner'), 
    path('drill_beginner_answer/<int:un>/<int:pk>', drill.DrillBeginnerAnswer.as_view(), name='drill_beginner_answer'),
    path('drill_beginners/<int:qn>/', drill.DrillBeginnerSeries.as_view(), name='drill_beginners'),
    path('drill_beginners_answer/<int:qn>/', drill.DrillBeginnerSeriesAnswer.as_view(), name='drill_beginners_answer'),
    path('compe/<int:pk>', compe.compe, name='compe'),
    path('compe_a/<int:pk>', compe.compe_a, name='compe_a'),
    path('p_like', compe.p_like, name='p_like'),
    path('p_like_ex', compe.p_like_ex, name='p_like_ex'),
    path('chapter', quartet.chapter, name='chapter'),
    path('q_list/<int:un>', quartet.q_list, name='q_list'),
    path('quartet/<int:un>/<int:pk>', quartet.quartet, name='quartet'),
    path('quartet_a/<int:un>/<int:pk>', quartet.quartet_a, name='quartet_a'),
    path('machine_learning', machine.machine_learning, name='machine_learning'),
    path('how_to', machine.how_to, name='how_to'),
] + [
    path('download/<int:pk>', machine.download, name='download')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()