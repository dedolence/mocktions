from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from django.urls import reverse_lazy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from ..models import User
from typing import Dict


class LoginTest(LiveServerTestCase):
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

    def _inputs(cls) -> Dict:
        return {
            "username": cls.driver.find_element(by=By.ID, value="id_username"),
            "password": cls.driver.find_element(by=By.ID, value="id_password"),
            "submit": cls.driver.find_element(by=By.CSS_SELECTOR, value="input[type='submit']")
        }

    def test_login(self) -> None:
        """
            Simple login loop:
            - start at index, 
            - click on login link, 
            - enter wrong credentials, 
            - enter correct credentials,
            - submit.
        """
        self.driver.get(self.live_server_url + reverse_lazy('base:index'))
        login_link = self.driver.find_element(by=By.LINK_TEXT, value="Login")
        login_link.click()


        # test wrong credentials
        self._inputs()["username"].send_keys('wrong_username')
        self._inputs()["password"].send_keys('wrong_password')
        self._inputs()["submit"].click()
        self.driver.implicitly_wait(1)
        error_message = self.driver.find_element(
            by=By.CSS_SELECTOR, 
            value="li[class='text-danger small']"
            )
        self.assertIn(
            "Please enter a correct username and password.", 
            error_message.text
            )

        self._inputs()["username"].clear()
        self._inputs()["password"].clear()
        self._inputs()["username"].send_keys('test_user')
        self._inputs()["password"].send_keys('test_password')
        self._inputs()["submit"].click()

        expected_url = self.live_server_url + reverse_lazy('accounts:profile', args=[self.user_id])
        
        actual_url = self.driver.current_url    # FULL url including host 
        self.assertEqual(actual_url, expected_url)


class RegisterTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def test_registration(self):
        self.driver.get(self.live_server_url + reverse_lazy('accounts:register'))
        