import unittest
import HtmlTestRunner
from test_suite import AdminTest
from test_suite import HomeTest
from test_suite import LoginTest
from test_suite import UploadTest
from test_suite import SignupTest
import sys
import os
from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname(__file__), '..')  # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, './test_cases')


# get all tests from SearchText and HomePageTest class
home_test = unittest.TestLoader().loadTestsFromTestCase(HomeTest)
login_test = unittest.TestLoader().loadTestsFromTestCase(LoginTest)
upload_test = unittest.TestLoader().loadTestsFromTestCase(UploadTest)
signup_test = unittest.TestLoader().loadTestsFromTestCase(SignupTest)
admin_test = unittest.TestLoader().loadTestsFromTestCase(AdminTest)
test_suite = unittest.TestSuite(
    [
        home_test, login_test, upload_test, signup_test, admin_test
    ]
)


# configure HTMLTestRunner options
runner = HtmlTestRunner.HTMLTestRunner(report_title='Test Report', combine_reports=True, open_in_browser=True,output='reports')

# run the suite using HTMLTestRunner
runner.run(test_suite)