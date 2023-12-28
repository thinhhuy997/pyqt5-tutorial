from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import requests

def get_2FA_Code(fa_secret: str):
    # URL with with the query param fa_scret
    url = f"https://2fa.live/tok/{fa_secret}"

    # A GET request to the API
    response = requests.get(url)

    # Return 2FA Code
    response_json = response.json()
    return response_json["token"]

options = webdriver.ChromeOptions() 
options.add_argument("user-data-dir=C:/Users/Thinh/Desktop/pyqt5-project/pyqt5-tutorial/user-profiles/google-chrome") #Path to your chrome profile
# w = webdriver.Chrome(chrome_options=options)
driver = webdriver.Chrome(
        # os.path.join(path, 'chromedriver'),
    options=options)

driver.get("https://www.facebook.com")

time.sleep(5)

driver.close()
# Find the username and password input fields and the login button using their respective attributes
username_input = driver.find_element(By.ID, "email")
password_input = driver.find_element(By.ID, "pass")
login_button = driver.find_element(By.NAME, "login")


# Enter your Facebook credentials
username_input.send_keys("61553087692402")
password_input.send_keys("hocat2kzl")

# Click the login button
login_button.click()

# Find the appovals_code field and checkPointSubmitbutton after click
appovals_code_input = driver.find_element(By.ID, "approvals_code")
checkPointSubmitbutton = driver.find_element(By.ID, "checkpointSubmitButton")

# GET 2FA Code
two_fa_code = get_2FA_Code("KXA7HGHXBY6AQGMRVSN2UJL74PCTAWIS")

# Enter 2FA Code
appovals_code_input.send_keys(two_fa_code)

# Click the CPS_button
checkPointSubmitbutton.click()

# Find checkbox
checkBox = driver.find_element(By.XPATH, "//div[@class='uiInputLabel clearfix uiInputLabelLegacy']/label")
# click check box
checkBox.click()



# find and click another CPS_Button
checkPointSubmitbutton = driver.find_element(By.ID, "checkpointSubmitButton")
checkPointSubmitbutton.click()

time.sleep(10)


driver.close()
