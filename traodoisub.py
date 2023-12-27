import requests


class Traodoisub:

    def __init__(self):
        self.base_url = "https://traodoisub.com"

    def get_cookie(self, username: str, password: str, proxy_string = None) -> str:
        # I'm Working here...
        target_url = "https://traodoisub.com/scr/login.php"

        form_data = {
            "username": username,
            "password": password,
        }

        if proxy_string:
            # Parse the proxy components
            ip, port, username, password = proxy_string.split(":")
            proxy_url = f"http://{username}:{password}@{ip}:{port}"

            proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }

            # Make a request using the proxy
            response = requests.post(target_url, data=form_data, proxies=proxies)
        else:
            # Make a request without using the proxy
            response = requests.post(target_url, data=form_data)

        cookie_string = ""

        for key, value in response.cookies.items():
            cookie_string = f"{key}={value};"
        
        return cookie_string
    
    def get_token(self, cookie: str) -> str:
        cookie_string = cookie.strip(";")

        # Split the cookie string into key and value
        cookie_key, cookie_value = cookie_string.split('=')

        # Create a dictionary with the cookie
        cookies = {cookie_key: cookie_value}

        # Make the request with the cookies
        response = requests.get("https://traodoisub.com/view/setting/load.php", cookies=cookies)

        response = response.json()

        tds_token, tds_coins = response["tokentds"], response["xu"]

        return tds_token, tds_coins
    
    def configure_facebook(self, facebook_id="", tds_token="", proxy_string = None):
        # response = requests.get(f'https://traodoisub.com/api/?fields=run&id={facebook_id}&access_token={tds_token}')
        # EX: https://traodoisub.com/api/?fields=run&id=100012702276792&access_token=TDS9JCOyVmdlNnI6IiclZXZzJCLiEzYjFGdzVGdzRGdiojIyV2c1Jye
        print('tds_token', tds_token)

        target_url = f"{self.base_url}/api/?fields=run&id={facebook_id}&access_token={tds_token}"

        if proxy_string:
            # Parse the proxy components
            ip, port, username, password = proxy_string.split(":")
            proxy_url = f"http://{username}:{password}@{ip}:{port}"

            proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }

            # Make a request using the proxy
            response = requests.get(target_url, proxies=proxies)
        else:
            # Make a request without the proxy
            response = requests.get(target_url)

        print("__tds_configure_facebook - response: ", response.json())


    # GET jobs with access token
    def get_facebook_jobs(self, tds_token="", proxy_string=None):

        target_url = f"{self.base_url}/api/?fields=like&access_token={tds_token}"
        

        if proxy_string:
            # Parse the proxy components
            ip, port, username, password = proxy_string.split(":")
            proxy_url = f"http://{username}:{password}@{ip}:{port}"

            proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }

            # Make a request using the proxy
            response = requests.get(target_url, proxies=proxies)
        else:
            response = requests.get(target_url)

        jobs = response.json()

        print('-------------------------------------')
        print('Jobs list:', jobs)
        print('-------------------------------------')

        if isinstance(jobs, dict):
            return []

        return jobs
    
    def get_job_coins(self, job_id="", tds_token="", proxy_string=None, tds_cookie=""):
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

        if proxy_string:
            # Parse the proxy components
            ip, port, username, password = proxy_string.split(":")
            proxy_url = f"http://{username}:{password}@{ip}:{port}"

            proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }

            # Make a request using the proxy
            response = requests.post(target_url, proxies=proxies, cookies=cookies, data=form_data)
        else:
            response = requests.post(target_url, cookies=cookies, data=form_data)

        return job_id, response.text