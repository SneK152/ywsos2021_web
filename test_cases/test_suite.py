import unittest
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import os
import time
from dotenv import load_dotenv
import random
from webdriver_manager.chrome import ChromeDriverManager
from random_word import RandomWords

r = RandomWords()
username_testchoice = r.get_random_word(minLength=7)
password_testchoice = r.get_random_word(minLength=7)

# HW workflow testing, fix admin testing
# HW clone ywsos2021_app into flutter and help w/ mbl
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

class AdminTest(unittest.TestCase):
    @classmethod
    def setUp(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        # options.add_argument('headless')
        cls.driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        cls.base_url = (os.getenv("DOMAIN")+"/login")
        cls.driver.get(cls.base_url)

    def test_adminEntry(self):
        self.driver.get(self.base_url)
        userInput = self.driver.find_element_by_id("username")
        userInput.send_keys(os.getenv("TESTUSER"))
        pwInput = self.driver.find_element_by_id("password")
        pwInput.send_keys(os.getenv("TESTPW"))
        submitButton = self.driver.find_element_by_id("submit")
        submitButton.click()
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - Account'))
        self.driver.get(os.getenv("DOMAIN") + "/admin")
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - Admin Panel'))

    def test_markResolved(self):
        self.driver.get(self.base_url)
        userInput = self.driver.find_element_by_id("username")
        userInput.send_keys(os.getenv("TESTUSER"))
        pwInput = self.driver.find_element_by_id("password")
        pwInput.send_keys(os.getenv("TESTPW"))
        submitButton = self.driver.find_element_by_id("submit")
        submitButton.click()
        self.driver.get(os.getenv("DOMAIN") + "/upload")
        titleInput = self.driver.find_element_by_id("title")
        titleInput.send_keys("Last Test")
        descInput = self.driver.find_element_by_id("desc")
        descInput.send_keys("Admin Test Description- Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. ")
        latInput = self.driver.find_element_by_id("lat")
        latInput.clear()
        latInput.send_keys("38.500102")
        longInput = self.driver.find_element_by_id("long")
        longInput.clear()
        longInput.send_keys("-122.699760")
        self.driver.find_element_by_id("file").send_keys(os.getcwd() + "/test_cases/test_image.jpeg")
        submitTest = self.driver.find_element_by_id("submit")
        submitTest.click()       
        self.assertIn("Form successfully submitted", self.driver.page_source)
        self.driver.get(os.getenv("DOMAIN") + "/admin")
        WebDriverWait(self.driver, 100)
        time.sleep(15)
        # markResolvedButton = self.driver.find_element_by_xpath("//p[contains(text(),'Admin Test Title, -122.69976')]")
        markResolvedButton = self.driver.find_element_by_id("Last Test38.500102")
        print(markResolvedButton)
        self.driver.execute_script("arguments[0].click();",markResolvedButton)
        self.assertIn("Resolved", self.driver.page_source)
 
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
        cls.base_url = (os.getenv("DOMAIN")+"/login")
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
        self.driver.get(os.getenv("DOMAIN") + "/main")
        logoutButton = self.driver.find_element_by_id("logout")
        logoutButton.click()
        self.assertTrue(expected_conditions.alert_is_present())
        self.driver.switch_to.active_element
        logoutButton1 = self.driver.find_element_by_id("logout")
        self.driver.execute_script("arguments[0].click();",logoutButton1)
        logoutButton2 = self.driver.find_element_by_id("confirmLogout")
        self.driver.execute_script("arguments[0].click();",logoutButton2)
        WebDriverWait(self.driver, 15).until(expected_conditions.title_is('GeoRepair - About'))

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
        cls.base_url = (os.getenv("DOMAIN")+"/upload")
        cls.driver.get(os.getenv("DOMAIN")+"/login")
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
        print(os.getcwd() + "test_image.jpeg")
        self.driver.find_element_by_id("file").send_keys("/Volumes/contents/ywsos2021_web/test_cases/test_image.jpeg")
        submitTest = self.driver.find_element_by_id("submit")
        submitTest.click()       
        self.assertIn("Form successfully submitted", self.driver.page_source)

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
        WebDriverWait(cls.driver, 15).until(expected_conditions.title_is('GeoRepair - Sign-up'))
    
    def test_signingup(self):
        usernameInput = self.driver.find_element_by_id("username")
        usernameInput.send_keys(username_testchoice)
        passwordInput = self.driver.find_element_by_id("password1")
        passwordInput.send_keys(password_testchoice)
        password2Input = self.driver.find_element_by_id("password2")
        password2Input.send_keys(password_testchoice)
        submitkey = self.driver.find_element_by_id("submit")
        submitkey.click()

    def test_signupduplicate(self):
        self.driver.get(os.getenv("DOMAIN") + "/signup")
        usernameInput = self.driver.find_element_by_id("username")
        usernameInput.send_keys(username_testchoice)
        passwordInput = self.driver.find_element_by_id("password1")
        passwordInput.send_keys(password_testchoice)
        password2Input = self.driver.find_element_by_id("password2")
        password2Input.send_keys(password_testchoice)
        submitkey = self.driver.find_element_by_id("submit")
        submitkey.click()
        self.assertIn("Username already exists", self.driver.page_source)

    @classmethod
    def tearDown(cls):
        cls.driver.quit()