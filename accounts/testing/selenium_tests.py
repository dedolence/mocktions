from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from django.urls import reverse_lazy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from ..models import User


class LoginFormTest(LiveServerTestCase):
    """
        Test the login loop:
        - visit index,
        - click on login, redirect,
        - enter credentials (incorrectly),
        - enter credentials (correctly),
        - redirect to index
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        cls.driver.implicitly_wait(10)
        cls.user = User.objects.create_user(
            username="test_user",
            password="test_password",
        )
        cls.user_id = cls.user.pk

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def test_login(self):
        """
            Simple login loop:
            - start at index, click on login link, enter credentials, submit.
        """
        self.driver.get(self.live_server_url + reverse_lazy('base:index'))
        login_link = self.driver.find_element(by=By.LINK_TEXT, value="Login")
        login_link.click()

        username_input = self.driver.find_element(by=By.ID, value="id_username")
        password_input = self.driver.find_element(by=By.ID, value="id_password")
        submit_input = self.driver.find_element(by=By.CSS_SELECTOR, value="input[type='submit']")

        username_input.send_keys('test_user')
        password_input.send_keys('test_password')
        submit_input.click()

        expected_url = self.live_server_url + reverse_lazy('accounts:profile', args=[self.user_id])
        actual_url = self.driver.current_url    # FULL url including host 
        self.assertEqual(actual_url, expected_url)