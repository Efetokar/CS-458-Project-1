import sqlite3
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class LoginTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        cls.conn = sqlite3.connect("users.db")
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute("SELECT email, phone, password FROM users")
        cls.valid_users = cls.cursor.fetchall()  

    def test_valid_logins(self):
        """Test login with valid credentials from the database"""
        driver = self.driver

        for user in self.valid_users:
            email, phone, password = user

            # Test login using email
            driver.get("http://127.0.0.1:5000/login")
            driver.find_element(By.ID, "user_input").clear()
            driver.find_element(By.ID, "user_input").send_keys(email)
            driver.find_element(By.ID, "password").clear()
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.TAG_NAME, "button").click()
            time.sleep(2)
            self.assertIn("welcome", driver.current_url.lower())
            driver.get("http://127.0.0.1:5000/logout")
            time.sleep(1)

            # Test login using telephone
            driver.get("http://127.0.0.1:5000/login")
            driver.find_element(By.ID, "user_input").clear()
            driver.find_element(By.ID, "user_input").send_keys(phone)
            driver.find_element(By.ID, "password").clear()
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.TAG_NAME, "button").click()
            time.sleep(2)
            self.assertIn("welcome", driver.current_url.lower())
            driver.get("http://127.0.0.1:5000/logout")
            time.sleep(1)

    def test_invalid_logins(self):
        """Test invalid login attempts"""
        driver = self.driver

        # Wrong email / correct password
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.ID, "user_input").clear()
        driver.find_element(By.ID, "user_input").send_keys("wrong@example.com")
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys("P@ssw0rd!")
        driver.find_element(By.TAG_NAME, "button").click()
        self.assertIn("error:", driver.page_source.lower())

        # Wrong telephone / correct password
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.ID, "user_input").clear()
        driver.find_element(By.ID, "user_input").send_keys("00000000000")
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys("P@ssw0rd!")
        driver.find_element(By.TAG_NAME, "button").click()
        self.assertIn("error:", driver.page_source.lower())

        # Blank fields
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.TAG_NAME, "button").click()
        self.assertIn("error:", driver.page_source.lower())

    def test_google_login(self):
        """Google OAuth test"""
        driver = self.driver
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.CLASS_NAME, "google-btn").click()
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
        self.assertIn("accounts.google.com", driver.current_url)

    def test_password_constraints(self):
        """Test password constraints (length and validity)"""
        driver = self.driver

        # Test with a too-long password (50+)
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.ID, "user_input").clear()
        driver.find_element(By.ID, "user_input").send_keys("test@example.com")
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys("a" * 300)
        driver.find_element(By.TAG_NAME, "button").click()
        self.assertIn("error", driver.page_source.lower())

        # Test with a too-short password (6-)
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.ID, "user_input").clear()
        driver.find_element(By.ID, "user_input").send_keys("test@example.com")
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys("a")
        driver.find_element(By.TAG_NAME, "button").click()
        self.assertIn("error", driver.page_source.lower())

        # Test with a password containing special characters
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.ID, "user_input").clear()
        driver.find_element(By.ID, "user_input").send_keys("test@example.com")
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys("P@ssw0rd!")
        driver.find_element(By.TAG_NAME, "button").click()
        self.assertNotIn("error", driver.page_source.lower())

    def test_injection_attacks(self):
        """Test SQL and XSS injection attacks"""
        driver = self.driver

        # SQL Injection attempt
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.ID, "user_input").clear()
        driver.find_element(By.ID, "user_input").send_keys("admin' OR '1'='1")
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys("P@ssw0rd!")
        driver.find_element(By.TAG_NAME, "button").click()
        self.assertIn("error", driver.page_source.lower())

        # XSS Injection attempt
        driver.get("http://127.0.0.1:5000/login")
        driver.find_element(By.ID, "user_input").clear()
        driver.find_element(By.ID, "user_input").send_keys("<script>alert('XSS')</script>")
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys("P@ssw0rd!")
        driver.find_element(By.TAG_NAME, "button").click()
        self.assertIn("error", driver.page_source.lower())

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.conn.close()

if __name__ == "__main__":
    unittest.main()
