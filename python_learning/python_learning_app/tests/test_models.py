from django.test import TestCase
from python_learning_app.models.questions import Basis, IntroCourse

class BasisModelTests(TestCase):

  def test_is_empty(self):
      """初期状態では何も登録されていないことをチェック"""  
      saved_posts = Basis.objects.all()
      self.assertEqual(saved_posts.count(), 0)