import unittest
from random_word import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv
import random
from webdriver_manager.chrome import ChromeDriverManager

# HW ADD ENV VARIABLES
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')  # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

class HomeTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument('headless')
        cls.driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        cls.base_url = os.getenv("DOMAIN")

    def test_home(self):
        self.driver.get(self.base_url )
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - About'))
        self.assertIn("Our App's Features", self.driver.page_source)
        
    def test_login(self):
        self.driver.get(self.base_url )
        loginButton = self.driver.find_element_by_id("login")
        loginButton.click()
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - Login'))
        self.assertIn("Sign In", self.driver.page_source)
    

    @classmethod
    def tearDown(cls):
        cls.driver.quit()

class LoginTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument('headless')
        cls.driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        cls.base_url = "http://127.0.0.1:5000/login"
        cls.driver.get(cls.base_url)

    def test_blanksubmission(self):
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - Login'))
        submitButton = self.driver.find_element_by_id("submit")
        submitButton.click()
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - Login'))
        self.assertIn("Sign In", self.driver.page_source)
        
    def test_usernameonly(self):
        self.driver.get(self.base_url)
        userInput = self.driver.find_element_by_id("username")
        userInput.send_keys("joe")
        submitButton = self.driver.find_element_by_id("submit")
        submitButton.click()
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - Login'))
        self.assertIn("Sign In", self.driver.page_source)
    
    def test_passwordonly(self):
        self.driver.get(self.base_url)
        pwInput = self.driver.find_element_by_id("password")
        pwInput.send_keys("11111")
        submitButton = self.driver.find_element_by_id("submit")
        submitButton.click()
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - Login'))
        self.assertIn("Sign In", self.driver.page_source)

    def test_correctcredentials(self):
        self.driver.get(self.base_url)
        userInput = self.driver.find_element_by_id("username")
        userInput.send_keys(os.getenv("TESTUSER"))
        pwInput = self.driver.find_element_by_id("password")
        pwInput.send_keys(os.getenv("TESTPW"))
        submitButton = self.driver.find_element_by_id("submit")
        submitButton.click()
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - Account'))

    @classmethod
    def tearDown(cls):
        cls.driver.quit()

class UploadTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument('headless')
        cls.driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        cls.base_url = "http://127.0.0.1:5000/upload"
        cls.driver.get("http://127.0.0.1:5000/login")
        userInput = cls.driver.find_element_by_id("username")
        userInput.send_keys(os.getenv("TESTUSER"))
        pwInput = cls.driver.find_element_by_id("password")
        pwInput.send_keys(os.getenv("TESTPW"))
        submitButton = cls.driver.find_element_by_id("submit")
        submitButton.click()
        WebDriverWait(cls.driver, 15).until(expected_conditions.title_is('GeoRepair - Account'))
        cls.driver.get(cls.base_url)

    def test_uploadCheck(self):
        titleInput = self.driver.find_element_by_id("title")
        titleInput.send_keys("Test Title")
        descInput = self.driver.find_element_by_id("desc")
        descInput.send_keys("Test Description- Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. ")
        latInput = self.driver.find_element_by_id("lat")
        latInput.send_keys("33.8658")
        longInput = self.driver.find_element_by_id("long")
        longInput.send_keys("151.2153")
        urgeTest = self.driver.find_element_by_id("urgency")
        urgeTest.send_keys("1")
        print(os.getcwd() + "test_image.jpeg")
        self.driver.find_element_by_id("file").send_keys("/Volumes/contents/ywsos2021_web/test_cases")
        submitTest = self.driver.find_element_by_id("submit")
        submitTest.click()
        self.assertIn("Form submitted", self.driver.page_source)

    @classmethod
    def tearDown(cls):
        cls.driver.quit()

class AccountTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument('headless')
        cls.driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        cls.driver.get(cls.base_url)
        userInput = cls.driver.find_element_by_id("username")
        userInput.send_keys(os.getenv("TESTUSER"))
        pwInput = cls.driver.find_element_by_id("password")
        pwInput.send_keys(os.getenv("TESTPW"))
        submitButton = cls.driver.find_element_by_id("submit")
        submitButton.click()
        WebDriverWait(cls.driver, 15).until(expected_conditions.title_is('GeoRepair - Account'))

    # left finished due to internal error with change password/username functionality

    @classmethod
    def tearDown(cls):
        cls.driver.quit()

class SignupTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument('headless')
        cls.driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        cls.driver.get(os.getenv("DOMAIN") + "/signup")
        WebDriverWait(cls.driver, 15).until(expected_conditions.title_is('GeoRepair - Signup'))
    
    def test_signingup(self):
        usernameInput = self.driver.find_element_by_id("username")
        usernameInput.send_keys(random_word())
        passwordInput = self.driver.find_element_by_id("password1")
        password_testchoice = random_word()
        passwordInput.send_keys(password_testchoice)
        password2Input = self.driver.find_element_by_id("password2")
        password2Input.send_keys(password_testchoice)
        submitkey = self.driver.find_element_by_id("submit")
        submitkey.click()

    # not further finished, internal error with change password/username functionality

    @classmethod
    def tearDown(cls):
        cls.driver.quit()