import requests


class Traodoisub:

    def __init__(self, proxy: dict):
        self.base_url = "https://traodoisub.com"
        self.proxy = proxy

    def configure_proxy(self, proxy: dict) -> dict:
        proxy_url = f"http://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"

        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }

        return proxies

    def get_cookie(self, username: str, password: str) -> str:

        proxies = self.configure_proxy(proxy=self.proxy)
        
        target_url = "https://traodoisub.com/scr/login.php"

        form_data = {
            "username": username,
            "password": password,
        }

        # Make a request using the proxy
        response = requests.post(target_url, data=form_data, proxies=proxies)

        cookie_string = ""

        for key, value in response.cookies.items():
            cookie_string = f"{key}={value};"
        
        return cookie_string
    
    def get_token(self, cookie: str) -> str:
        proxies = self.configure_proxy(proxy=self.proxy)

        cookie_string = cookie.strip(";")

        # Split the cookie string into key and value
        cookie_key, cookie_value = cookie_string.split('=')

        # Create a dictionary with the cookie
        cookies = {cookie_key: cookie_value}

        # Make the request with the cookies and proxies
        response = requests.get("https://traodoisub.com/view/setting/load.php", cookies=cookies, proxies=proxies)

        response = response.json()

        tds_token, tds_coins = response["tokentds"], response["xu"]

        return tds_token, tds_coins
    
    def configure_facebook(self, cookie:str, facebook_id:str):
        # response = requests.get(f'https://traodoisub.com/api/?fields=run&id={facebook_id}&access_token={tds_token}')
        # EX: https://traodoisub.com/api/?fields=run&id=100012702276792&access_token=TDS9JCOyVmdlNnI6IiclZXZzJCLiEzYjFGdzVGdzRGdiojIyV2c1Jye

        target_url = f"{self.base_url}/scr/datnick.php"

        proxies = self.configure_proxy(proxy=self.proxy)

        cookie_string = cookie.strip(";")

        # Split the cookie string into key and value
        cookie_key, cookie_value = cookie_string.split('=')

        # Create a dictionary with the cookie
        cookies = {cookie_key: cookie_value}

        form_data = {
            "iddat": facebook_id,
        }

        # Make a request using the proxy
        response = requests.post(target_url, data=form_data, proxies=proxies, cookies=cookies)

        return response.text


    def get_facebook_id(self, url: str):
        target_url = 'https://id.traodoisub.com/api.php'
    
        proxies = self.configure_proxy(proxy=self.proxy)

        form_data = {
            "link": url,
        }

        response = requests.post(target_url, proxies=proxies, data=form_data)

        return response.json()

    # GET jobs with access token
    def get_facebook_jobs(self, tds_token=""):

        proxies = self.configure_proxy(proxy=self.proxy)
        target_url = f"{self.base_url}/api/?fields=like&access_token={tds_token}"
        
        # Make a request using the proxy
        response = requests.get(target_url, proxies=proxies)

        jobs = response.json()

        # if isinstance(jobs, dict):
        #     return []

        # if error jobs is a dict {} else jobs is a list []

        return jobs
    
    def get_job_coins(self, job_id="", tds_cookie=""):
        proxies = self.configure_proxy(proxy=self.proxy)

        target_url = f"{self.base_url}/ex/like/nhantien.php"

        cookie_string = tds_cookie.strip(";")

        # Split the cookie string into key and value
        cookie_key, cookie_value = cookie_string.split('=')

        # Create a dictionary with the cookie
        cookies = {cookie_key: cookie_value}
        

        form_data = {
            'id': job_id,
            'type': "like",
        }

        # Make a request using the proxy
        response = requests.post(target_url, proxies=proxies, cookies=cookies, data=form_data)

        return job_id, response.text
    