import requests
import time
import json
import threading
from pymongo import MongoClient
from bs4 import BeautifulSoup
from lxml import html
from queue import Queue
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def launch_page(issue):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path = '/usr/local/bin/geckodriver', options = options)

    for i in range(1, issue + 1):
        url = f'https://www.bilibili.com/v/popular/weekly?num={i}'
        driver.get(url)
        print(f'now loading No.{i}:')
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "video-card")))
            response = driver.page_source
            soup = BeautifulSoup(response, 'lxml')
            video_hrefs = soup.find_all('div', class_ = 'video-card')
            for sub in video_hrefs:
                href = sub.find('a', href = True)['href']
                print(f'href:{href}')
                q.put(href)
        except TimeoutException:
            print('等待超时')
    driver.quit()
    end_event.set()

def get_video_info():
    while True:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            if q.empty() and end_event.is_set():
                break
            href = q.get()
            if not isinstance(href, str):
                q.task_done()
                if end_event.is_set():
                    break
                continue
            response = requests.get('https:' + href, headers = headers)
            soup = BeautifulSoup(response.text, 'lxml')
            a_tags = soup.find_all('a', class_ = 'tag-link')
            title = soup.find('h1', class_ = 'video-title')
            pubtime = soup.find('span', class_ = 'pubdate-text')
            video_tags = []
            for tag in a_tags:
                href = tag.get('href')
                if href.startswith('//www.bilibili.com/v'):
                    video_tags.append(tag.get_text())
            if title and pubtime:
                info = {
                    'video_title': title.get_text(),
                    'video_time':  pubtime.get_text().strip(),
                    'video_tags': video_tags
                }
                print(f'info collected: {info}')
                tb.insert_one(info)
        
        except queue.Empty:
            continue
        except requests.HTTPError as e:
            print(f"HTTP error: {e}")
        except Exception as e:
            print(f"Other error: {e}")

        finally:
            if not q.empty():
                q.task_done()

print("正在连接MongoDB")
client = MongoClient("mongodb://nooboo:luoyuyang@localhost:27017/")
db = client["biliStat"]
tb = db['videoInfo']
q = Queue()
end_event = threading.Event()
T = []

issue = input('连接正常\n想从第1期爬到第几期？')
start_time = time.time()
issue = int(issue)

threading.Thread(target = launch_page, args = (issue, )).start()
for i in range(3):
    t = threading.Thread(target = get_video_info)
    t.start()
    T.append(t)

# q.join()
for t in T:
    t.join()

end_time = time.time()
print(f'程序运行用时：{end_time - start_time}秒')
