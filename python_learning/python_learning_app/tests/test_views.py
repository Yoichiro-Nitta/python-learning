from django.test import TestCase
from django.urls import reverse, resolve
from python_learning_app.models.questions import Basis, IntroCourse
from python_learning_app.models.index import CustomUser, News
from python_learning_app.forms import SignupForm
from python_learning_app.views.index import SignupView
from python_learning_app.views.intro import IntroCourseView

# Create your tests here.

class SignUpTests(TestCase):
    def setUp(self):
        url = reverse('python_learning:signup_view')
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/signup_view')
        self.assertEqual(view.func.view_class, SignupView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignupForm)

class IntroCourseTests(TestCase):
    def setUp(self):
        IntroCourse.objects.create(title = 'テスト', section = 1, order = 1)
        url = reverse('python_learning:intro_ex', kwargs = {'pk': 1})
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)
        
    def test_context(self):
        next_num = self.response.context.get('next_num')
        self.assertEqual(next_num, 2)


class DrillBeginnerTests(TestCase):
    def setUp(self):
        self.url = reverse('python_learning:drill_beginner', kwargs = {'un': 1, 'pk': 1})
        self.response = self.client.get(self.url)

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 302)

    def test_index_status_code(self):
        query = '?next=' + self.url 
        login_req = reverse('python_learning:login_req') + query
        self.assertRedirects(self.response, login_req)