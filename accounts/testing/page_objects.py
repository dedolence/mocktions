from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# for relative locators, above, below, near, etc.
from selenium.webdriver.support.relative_locator import locate_with

# for type hinting
from selenium.webdriver.remote.webelement import WebElement


class BasePageObject():
    def __init__(self, driver: webdriver.Firefox | webdriver.Chrome) -> None:
        self.driver = driver


class RegistrationPage(BasePageObject):
    def __init__(self, driver) -> None:
        super().__init__(driver)
        self.username_field = self.driver.find_element(By.ID, "id_username")
        self.password1_field = self.driver.find_element(By.ID, "id_password1")
        self.password2_field = self.driver.find_element(By.ID, "id_password2")
        self.first_name_field = self.driver.find_element(By.ID, "id_first_name")
        self.last_name_field = self.driver.find_element(By.ID, "id_last_name")
        self.email_field = self.driver.find_element(By.ID, "id_email")
        self.street_field = self.driver.find_element(By.ID, "id_street")
        self.city_field = self.driver.find_element(By.ID, "id_city")
        self.state_field = self.driver.find_element(By.ID, "id_state")
        self.postcode_field = self.driver.find_element(By.ID, "id_postcode")
        self.country_field = self.driver.find_element(By.ID, "id_country")
        self.phone_field = self.driver.find_element(By.ID, "id_phone")
        self.submit_button = self.driver.find_element(
            By.CSS_SELECTOR, "input[type='submit']"
        )

        self.wait = WebDriverWait(self.driver, timeout=10)
    
    def register_user_success(
                self, 
                username: str, 
                password: str) -> "LoginPage":
        self.username_field.send_keys(username)
        self.password1_field.send_keys(password)
        self.password2_field.send_keys(password)
        self.click_submit()
        return LoginPage(self.driver)

    def register_user_failure(
        self,
        username: str,
        password: str
    ) -> "RegistrationPage":
        self.username_field.send_keys(username)
        self.password1_field.send_keys(password)
        self.password2_field.send_keys(password)
        self.click_submit()
        return RegistrationPage(self.driver)


    def get_username_error(self) -> WebElement:
        return self.driver.find_element(
            locate_with(By.TAG_NAME, "li").near(self.username_field)
        )

    def get_password_error(self) -> WebElement:
        return self.driver.find_element(
            locate_with(By.TAG_NAME, "li").near(self.password2_field)
        )

    def click_submit(self):
        """
            Putting this here because for some reason no other means of 
            clicking this button works!
        """
        self.driver.execute_script("arguments[0].click()", self.submit_button)


class LoginPage(BasePageObject):
    def __init__(self, driver) -> None:
        super().__init__(driver)
        self.username_field = self.driver.find_element(By.ID, "id_username")
        self.password_field = self.driver.find_element(By.ID, "id_password")
        self.submit_button = self.driver.find_element(
            By.CSS_SELECTOR, "input[type='submit']"
        )
    
    def click_submit(self):
        """
            Putting this here because for some reason no other means of 
            clicking this button works!
        """
        self.driver.execute_script("arguments[0].click()", self.submit_button)

    def login_user(self, 
                   username: str, 
                   password: str, 
                   fail: bool = False
                ) -> "IndexPage":
        self.username_field.send_keys(username)
        self.password_field.send_keys(password)
        self.click_submit()
        return IndexPage(self.driver)




class IndexPage(BasePageObject):
    def __init__(self, driver) -> None:
        super().__init__(driver)