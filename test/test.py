
import threading 
from selenium import webdriver
import time
  
class ScrapeThread(threading.Thread): 
    def __init__(self, thread_index, delay): 
        threading.Thread.__init__(self) 
        # self.url = url
        self.thread_index = thread_index
        self.delay = delay

    def test(self, thread_index):
        for i in range(3):
            print(f"Luồng số {thread_index} đang chạy vòng i = ", i)
            time.sleep(self.delay)
  
    def run(self):
        self.test(self.thread_index)
        # driver = webdriver.Chrome() 
        # driver.get(self.url) 
        # page_source = driver.page_source 
        # driver.close() 
        # do something with the page source 


    
  
urls = [ 
    'https://en.wikipedia.org/wiki/0', 
    'https://en.wikipedia.org/wiki/1', 
    'https://en.wikipedia.org/wiki/2', 
    'https://en.wikipedia.org/wiki/3', 
]

ts = [0, 1, 2, 3]
  
threads = [] 
# for url in urls: 
#     t = ScrapeThread(url) 
#     t.start() 
#     threads.append(t) 

for index in ts:
    if index % 2 == 0:
        delay = 1
    else:
        delay = 2 
    t = ScrapeThread(index, delay) 
    t.start() 
    threads.append(t)
  
for t in threads: 
    t.join()