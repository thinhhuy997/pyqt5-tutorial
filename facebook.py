from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PyQt5.QtCore import Qt, QRunnable, QObject, pyqtSlot, pyqtSignal, QThreadPool
import requests
from PyQt5.QtCore import QObject, pyqtSignal
import time
from proxy_chrome_driver import get_chromedriver
from auto_action import auto_like, auto_haha, auto_play_video, auto_comment_on_livetream, auto_follow_on_livestream
import traceback

from traodoisub import Traodoisub

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

    coins = pyqtSignal(object)

class SeleniumWorker(QRunnable):
    
    # driver = get_chromedriver(use_proxy=False, user_agent=None, host=None, port=None, username=None, password=None)

    # actions list will be like this: {'type': 'like', 'jobs': ['url_1', 'url_2', ...]}

    

    def __init__(self, facebook_login_credential: dict, tds_login_credential: dict, action: dict):
        super(SeleniumWorker, self).__init__()

        # new
        self.facebook_login_credential = facebook_login_credential

        # new
        self.tds_login_credential = tds_login_credential

        self.action = action

        self.signals = WorkerSignals()

        self.traodoisub = Traodoisub()

        self.driver = get_chromedriver(use_proxy=False, user_agent=None, host=None, port=None, username=None, password=None)


    @pyqtSlot()
    def run(self):
        try:
            # Initialize Selenium WebDriver (you may need to adjust the path to your WebDriver)
            # driver = webdriver.Chrome()

            # Perform some simple action (e.g., login facebook, get tds_cookie, etc...)
            self.login()

            # Simulate a delay (e.g., to simulate a time-consuming task)
            time.sleep(2)

            # _______________GET TDS COOKIE________________
            tds_cookie = self.traodoisub.get_cookie(username=self.tds_login_credential['username'], 
                                                    password=self.tds_login_credential['password'])
            
            self.signals.result.emit(f'tds_cookie: {tds_cookie}')
            
            # ________________GET TDS TOKEN_________________
            tds_token, tds_coins = self.traodoisub.get_token(cookie=tds_cookie)
            # update table with coins
            self.signals.coins.emit(tds_coins)


            # time.sleep(1000)


            # target_url = "https://www.facebook.com"

            # if self.action['type'] == 'like' and len(self.action['jobs']) > 0:
            #     self.signals.result.emit('Executing jobs from TRAODOISUB...')
            #     jobs = self.action['jobs']

            #     for i, job in enumerate(jobs):
            #         self.open_new_tab_and_interact(url=f'{target_url}/{job["id"]}', like=True, tab_order=(i+1), delay=10)
            #         job_id, response_msg = self.traodoisub.get_job_coins(job_id=job["id"], tds_cookie=self.tds_cookie)
            #         msg = f"Job ID: {job_id} - {response_msg}"
            #         self.signals.result.emit(msg)

            

            # Emit the result signal
            # self.signals.result.emit(f"Task completed for {self.url}")

        except Exception as e:
            # Emit the error signal if an exception occurs
            tb_info = traceback.format_exc()
            self.signals.error.emit((type(e), e.args, tb_info))

        # finally:
            # Close the WebDriver
            # driver.quit()

            # Emit the finished signal
            # self.signals.finished.emit()


    def login(self):
        try:
            self.signals.result.emit('Signing in facebook...')
            # Navigate to the Facebook login page
            self.driver.get("https://www.facebook.com")

            time.sleep(5)

            # Find the username and password input fields and the login button using their respective attributes
            username_input = self.driver.find_element(By.ID, "email")
            password_input = self.driver.find_element(By.ID, "pass")
            login_button = self.driver.find_element(By.NAME, "login")


            # Enter your Facebook credentials
            username_input.send_keys(self.facebook_login_credential["uid"])
            password_input.send_keys(self.facebook_login_credential["password"])

            # Click the login button
            login_button.click()

            # Find the appovals_code field and checkPointSubmitbutton after click
            appovals_code_input = self.driver.find_element(By.ID, "approvals_code")
            checkPointSubmitbutton = self.driver.find_element(By.ID, "checkpointSubmitButton")

            # GET 2FA Code
            two_fa_code = self.get_2FA_Code(self.facebook_login_credential["fa_secret"])

            # Enter 2FA Code
            appovals_code_input.send_keys(two_fa_code)

            # Click the CPS_button
            checkPointSubmitbutton.click()

            # Find checkbox
            checkBox = self.driver.find_element(By.XPATH, "//div[@class='uiInputLabel clearfix uiInputLabelLegacy']/label")
            # click check box
            checkBox.click()



            # find and click another CPS_Button
            checkPointSubmitbutton = self.driver.find_element(By.ID, "checkpointSubmitButton")
            checkPointSubmitbutton.click()

            time.sleep(2)
        
        except Exception as error:
            self.signals.result.emit(error)

        
        self.signals.result.emit('Signed in facebook successfully!')


        

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
            self.signals.error.emit(error)

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