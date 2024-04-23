from selenium import webdriver # ←このインポート文だけでOK
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

class UiTest(StaticLiveServerTestCase):
  fixtures = ['python_learning_app/fixtures/Basis.json']

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    # options = Options()
    # 3. setUpClass内でブラウザを起動
    # options.add_argument('--no-sandbox')  # UIのないOSの場合首開けすること
    # options.add_argument('--headless')    # UIのないOSの場合首開けすること
    cls.selenium = webdriver.Chrome()

  @classmethod
  def tearDownClass(cls):
    # 4. tearDownClass内でブラウザを終了させる
    cls.selenium.quit()
    super().tearDownClass()
  
  def test_1(self):
    UiTest.selenium.get("https://www.google.com/")
    sleep(3)
    UiTest.selenium.close()
    UiTest.selenium.quit()
    

"""参考コード
driver = webdriver.Chrome() # これだけでOK（optionsを入れる場合はカッコ内に入れます。）
driver.get("https://www.google.com/")
sleep(3)

driver.close()
driver.quit()
"""