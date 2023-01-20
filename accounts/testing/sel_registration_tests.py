from pathlib import Path

from django.test import LiveServerTestCase
from django.urls import reverse_lazy

from selenium import webdriver

# use these instead of executable_path
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chromium.service import ChromiumService

# for installing the specific browser drivers
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager

from .page_objects import RegistrationPage, LoginPage, IndexPage
from ..models import User

from django.contrib.auth.password_validation import password_validators_help_texts as password_help_texts

from time import sleep

""" ff_options = webdriver.FirefoxOptions()
ff_options.headless = True
ff_driver = webdriver.Firefox(
    service = FirefoxService(GeckoDriverManager().install()),
    options = ff_options
)
ff_driver.timeouts.implicit_wait = 10
ff_driver.set_page_load_timeout(10) """

ch_options = webdriver.ChromeOptions()
ch_options.headless = True
ch_driver = webdriver.Chrome(
    service = ChromiumService(ChromeDriverManager().install()),
    options = ch_options
)
ch_driver.timeouts.implicit_wait = 10
ch_driver.set_page_load_timeout(10)

class Registration(LiveServerTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.driver = ch_driver
        cls.username = "test_user"
        cls.password = "vTooGyk5"
        super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self) -> None:
        self.driver.get(
            self.live_server_url + reverse_lazy("accounts:register")
        )
        self.reg_page = RegistrationPage(self.driver)
    
    def test_registration_basic_success(self):
        self.reg_page.username_field.send_keys(self.username)
        self.reg_page.password1_field.send_keys(self.password)
        self.reg_page.password2_field.send_keys(self.password)
        self.reg_page.click_submit()
        
        self.assertEqual(
            self.live_server_url + reverse_lazy("accounts:login"),
            self.driver.current_url
        )
        self.assertEqual(
            User.objects.all().count(), 1
        )
        self.assertEqual(
            User.objects.get().username,
            self.username
        )

    def test_registration_duplicate_username(self):
        user = User.objects.create_user(self.username, self.password)
        
        self.reg_page.username_field.send_keys(self.username)
        self.reg_page.password1_field.send_keys(self.password)
        self.reg_page.password2_field.send_keys(self.password)
        self.reg_page.click_submit()

        # refresh page since now it has error messages
        self.reg_page = RegistrationPage(self.driver)

        reg_error = self.reg_page.get_username_error()
        self.assertIn(
            "A user with that username already exists", 
            reg_error.text
        )

    def test_password_similarity(self):
        self.reg_page = RegistrationPage(self.driver)
        self.reg_page.first_name_field.send_keys("Nathaniel")
        self.reg_page.last_name_field.send_keys("Hoyt")
        self.reg_page.username_field.send_keys(self.username)
        self.reg_page.password1_field.send_keys("Nathaniel123!")
        self.reg_page.password2_field.send_keys("Nathaniel123!")
        self.reg_page.click_submit()

        self.reg_page = RegistrationPage(self.driver)
        reg_error = self.reg_page.get_password_error()
        self.assertIn(
            "The password is too similar to the",
            reg_error.text
        )

    def test_password_strength(self):
        self.reg_page.register_user_failure(self.username, "password")

        self.reg_page = RegistrationPage(self.driver)
        reg_error = self.reg_page.get_password_error()
        self.assertIn(
            "This password is too common",
            reg_error.text
        )

    def test_password_alphanumeric(self):
        self.reg_page.register_user_failure(self.username, "39829834792837")

        self.reg_page = RegistrationPage(self.driver)
        reg_error = self.reg_page.get_password_error()
        self.assertIn(
            "entirely numeric",
            reg_error.text
        )