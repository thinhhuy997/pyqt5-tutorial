from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
from PyQt5.QtCore import QObject, pyqtSignal
import time
from proxy_chrome_driver import get_chromedriver
from auto_action import auto_like, auto_haha, auto_play_video, auto_comment_on_livetream, auto_follow_on_livestream
import threading


class SeleniumWorker(QObject):
    # def __init__(self):

    #     self.driver = webdriver.Chrome()

    #     self.progressLogin = pyqtSignal(str)

    driver = webdriver.Chrome()

    progressLogin = pyqtSignal(str)
    job_msg = pyqtSignal(str)  # message to be shown to user

    def doWork(self):
        driver_test = webdriver.Chrome()
        for i in range(10):
            driver_test.get(f'https://www.facebook.com/{i}')
            time.sleep(5)

    def login(self, account_credentials = {}):
        
        # Navigate to the Facebook login page
        self.driver.get("https://www.facebook.com")

        time.sleep(30)

        # Find the username and password input fields and the login button using their respective attributes
        username_input = self.driver.find_element(By.ID, "email")
        password_input = self.driver.find_element(By.ID, "pass")
        login_button = self.driver.find_element(By.NAME, "login")


        # Enter your Facebook credentials
        username_input.send_keys(account_credentials["uid"])
        password_input.send_keys(account_credentials["password"])

        # Click the login button
        login_button.click()

        # Find the appovals_code field and checkPointSubmitbutton after click
        appovals_code_input = self.driver.find_element(By.ID, "approvals_code")
        checkPointSubmitbutton = self.driver.find_element(By.ID, "checkpointSubmitButton")

        # GET 2FA Code
        two_fa_code = self.get_2FA_Code(account_credentials["fa_secret"])

        # Enter 2FA Code
        appovals_code_input.send_keys(two_fa_code)

        # Click the CPS_button
        checkPointSubmitbutton.click()

        # Find checkbox
        try:
            checkBox = self.driver.find_element(By.XPATH, "//div[@class='uiInputLabel clearfix uiInputLabelLegacy']/label")
            # click check box
            checkBox.click()
        except Exception as error:
            print(error)

        # find and click another CPS_Button
        try:
            checkPointSubmitbutton = self.driver.find_element(By.ID, "checkpointSubmitButton")
            checkPointSubmitbutton.click()
        except Exception as error:
            print(error)

        # new
        self.progressLogin.emit('Đăng nhập thành công!')

        time.sleep(2)


        

    def open_new_tab(self, url="/"):
        self.driver.execute_script(f"window.open('{url}');")

    def quit_driver(self):
        self.driver.quit()

    def clear_browser(self):
        # Clear cookies
        self.driver.delete_all_cookies()

        # Clear localStorage
        self.driver.execute_script("localStorage.clear();")

        # Clear sessionStorage
        self.driver.execute_script("sessionStorage.clear();")

        # Switch to the parent tab
        self.driver.switch_to.window(self.driver.window_handles[0])

        # Close all remaining tabs
        for handle in self.driver.window_handles[1:]:
            self.driver.switch_to.window(handle)
            self.driver.close()

        # Switch to the parent tab
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.driver.refresh()

    def get_2FA_Code(self, fa_secret: str):
        # URL with with the query param fa_scret
        url = f"https://2fa.live/tok/{fa_secret}"

        # A GET request to the API
        response = requests.get(url)

        # Return 2FA Code
        response_json = response.json()
        return response_json["token"]

    def like_some_post(self, post_count: int):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Thích']")))
            like_buttons = self.driver.find_elements(By.XPATH, "//div[@aria-label='Thích']")
            print("count:", len(like_buttons))

            count = 0

            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Thích']"))).click()

            for like_button in like_buttons:
                if count <= post_count:
                    like_button.click()

                    # increase count
                    count += 1

                    # sleep in 2 seconds
                    time.sleep(2)
                else:
                    break
        except Exception as error:
            print(error)

    def comment_some_post(self, post_count: int):
        try:
            show_comment_box_buttons = self.driver.find_elements(By.XPATH, "//div[@aria-label='Viết bình luận']")

            print("show_comment_box_buttons' count:", len(show_comment_box_buttons))

            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Viết bình luận']"))).click()

            
            for s_c_b_button in show_comment_box_buttons:
                # check
                # //div[@aria-label='Đóng']

                # click
                s_c_b_button.click()

                

                # check length of close buttons (2 if is dialog show and other hand)
            
                if len(self.driver.find_elements(By.XPATH, "//div[@aria-label='Đóng']")) == 2:
                    print('TRUE')
                    WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Đóng']"))).click()


                    self.driver.find_elements(By.XPATH, "//div[@aria-label='Đóng']")[1].click()

                

                # sleep in 2 seconds
                time.sleep(2)
            
        except Exception as error:
            print(error)

    def scroll_down_continuous(self, driver, scroll_delay=2, num_scrolls=None):
        # Define the scroll script
        scroll_script = "window.scrollTo(0, document.body.scrollHeight);"

        try:
            scroll_count = 0
            while num_scrolls is None or scroll_count < num_scrolls:
                # Execute the scroll script
                driver.execute_script(scroll_script)

                # Interacting

                
                # Wait for a short time to allow the content to load
                time.sleep(scroll_delay)

                scroll_count += 1
        except KeyboardInterrupt:
            # Handle interruption with KeyboardInterrupt (Ctrl+C)
            pass

    def open_new_tab_and_interact(self, url='', like=False, comment=False, tab_order = 0, delay=2):

        try:
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            
            
            # Switch to second tab ~ correspond index is 1 (parent tab is 0)
            # In this case, index 1 corresponds to the second tab (since indexing starts from 0)
            self.driver.switch_to.window(self.driver.window_handles[tab_order])


            if like:
                try:
                    WebDriverWait(self.driver, 6).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Thích']"))).click()
                    time.sleep(2)
                except Exception as error:
                    print(error)

            if comment:
                try:
                    time.sleep(2)
                    WebDriverWait(self.driver, 6).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Viết bình luận']"))).click()

                    # Locate comment box
                    comment_box = self.driver.find_element(By.XPATH, "//div[@aria-label='Viết bình luận...']/p")

                    # Enter into comment box
                    comment_box.send_keys('Xin chào')

                    # Hit ENTER
                    comment_box.send_keys(Keys.RETURN)
                except Exception as error:
                    print(error)

            # Sleep time between jobs
            time.sleep(delay)

        except Exception as error:
            print(error)

    def watch_livestream_and_interact(self, url='', like=False, comment=False, delay=2):
        time.sleep(delay)

        try:
            # open new tab
            self.driver.execute_script(f"window.open('{url}');")
            # Switch to second tab ~ correspond index is 1 (parent tab is 0)
            # In this case, index 1 corresponds to the second tab (since indexing starts from 0)
            self.driver.switch_to.window(self.driver.window_handles[1])

            # auto_like(driver, delay_action=5)


            # auto_play_video(driver=driver, delay_action=5)

            # auto_haha(driver, delay_action=5)
            # auto_comment_on_livetream(driver=driver, delay_action=5)

            auto_follow_on_livestream(self.driver, delay_action=5)

            # //div[@aria-label='Phát video']

            # Play video (live stream)
            # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Phát video']"))).click()
            

        except Exception as error:
            print(error)

    def get_cookie_and_write_it_into_file(self, file_name:str):
        cookies = self.driver.get_cookies()

        fb_cookie_str = ""

        for cookie in cookies:
            fb_cookie_str += cookie['name'] + '=' + cookie['value'] + ';'
        if file_name:
            with open(file_name, 'w') as file:
                # Write fb_cookie_str to the file
                file.write(fb_cookie_str)

            print('Wrote facebook cookie successfully!')