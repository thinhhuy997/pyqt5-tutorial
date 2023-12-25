from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from enum import Enum
from selenium.webdriver.common.keys import Keys
import time



def auto_like(driver = None, delay_action = None):
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Thích']"))).click()

        if delay_action:
            time.sleep(delay_action)

    except Exception as error: 
        print(error)

def auto_love(driver = None, delay_action = None):
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Yêu thích']"))).click()

        if delay_action:
            time.sleep(delay_action)

    except Exception as error: 
        print(error)

def auto_thuongthuong(driver = None, delay_action = None):
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Thương thương']"))).click()

        if delay_action:
            time.sleep(delay_action)

    except Exception as error: 
        print(error)
    
def auto_haha(driver = None, delay_action = None):
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Haha']"))).click()

        if delay_action:
            time.sleep(delay_action)

    except Exception as error: 
        print(error)

def auto_wow(driver = None, delay_action = None):
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Wow']"))).click()

        if delay_action:
            time.sleep(delay_action)

    except Exception as error: 
        print(error)

def auto_sad(driver = None, delay_action = None):
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Buồn']"))).click()

        if delay_action:
            time.sleep(delay_action)

    except Exception as error: 
        print(error)

def auto_angry(driver = None, delay_action = None):
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Phẫn nộ']"))).click()

        if delay_action:
            time.sleep(delay_action)

    except Exception as error: 
        print(error)

def auto_play_video(driver = None, delay_action = None):
    try:
        # WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Phát video']/.."))).click()

        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Phát video']/..")))
        driver.execute_script("arguments[0].click();", button)

        if delay_action:
            time.sleep(delay_action)

    except Exception as error:
        print(error)

def auto_comment_on_livetream(driver = None, delay_action = None):
    try:
        # Click Show Comment Button to show comment box
        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Viết bình luận']"))).click()


        # Locate comment box
        comment_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Viết bình luận...']/p")))
        comment_box.send_keys('tương tác nào!')

        time.sleep(2)

        # Hit ENTER
        comment_box.send_keys(Keys.RETURN)

        if delay_action:
            time.sleep(delay_action)

    except Exception as error:
        print(error)

def auto_follow_on_livestream(driver=None, delay_action=None):
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Theo dõi']"))).click()

        if delay_action:
            time.sleep(delay_action)

    except Exception as error: 
        print(error)
