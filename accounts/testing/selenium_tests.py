from django.test import LiveServerTestCase
from django.urls import reverse_lazy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from ..models import User

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

class LoginFormTest(LiveServerTestCase):
    fixtures = ['user_fixtures.json']

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.selenium = webdriver.Firefox()
        cls.selenium.implicitly_wait(10)

    """ @classmethod
    def tearDownClass(cls) -> None:
        cls.selenium.quit()
        super().tearDownClass() """

    def test_form(self):

        self.selenium.get('%s%s' % (self.live_server_url, reverse_lazy('accounts:login')))

        username_input = self.selenium.find_element(by=By.ID, value="id_username")
        password_input = self.selenium.find_element(by=By.ID, value="id_password")
        submit_input = self.selenium.find_element(by=By.CSS_SELECTOR, value='input[type="submit"]')

        username_input.send_keys("dedolence")
        password_input.send_keys("chicken")
        submit_input.send_keys(Keys.RETURN)

        assert "/accounts/profile/1" in self.selenium.current_url