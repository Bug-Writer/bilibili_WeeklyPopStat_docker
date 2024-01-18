import requests
import time
import json
from pymongo import MongoClient
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def launch_page(issue):
    options = Options()
    options.headless = True
    url = f'https://www.bilibili.com/v/popular/weekly?num={issue}'
    driver = webdriver.Firefox(executable_path = '/usr/local/bin/geckodriver', options = options)
    driver.get(url)
    
    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "video-card")))
    finally:
        print(f'now loading No.{issue}:')
        response = driver.page_source
        driver.quit()

    soup = BeautifulSoup(response, 'html.parser')
    video_hrefs = soup.find_all('div', class_ = 'video-card')
    # print(f'video_hrefs found: {video_hrefs}')

    if not video_hrefs:
        return "find no video href."

    sub_hrefs = []
    for sub in video_hrefs:
        tmp = sub.find('a', href = True)
        sub_hrefs.append(tmp['href'])

    # print(f'sub_hrefs found: {sub_hrefs}')

    info = []
    for href in sub_hrefs:
        tmp = get_video_info('https:' + href)
        data_dict = {
            'video_title': tmp[0],
            'video_time':  tmp[1],
            'video_tags':  tmp[2]
        }
        info.append(data_dict)

    return info

def get_video_info(href):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        # print('loading function get_video_tags...')
        response1 = requests.get(href, headers = headers)
        soup1 = BeautifulSoup(response1.text, 'html.parser')
        a_tags = soup1.find_all('a', class_ = 'tag-link')
        title = soup1.find('h1', class_ = 'video-title').get_text()
        pubtime = soup1.find('span', class_ = 'pubdate-text').get_text().strip()
        video_tags = []
        for tag in a_tags:
            href = tag.get('href')
            if href.startswith('//www.bilibili.com/v'):
                video_tags.append(tag.get_text())
        info = [title, pubtime, video_tags]
        print(f'info collected: {info}')
    
    except requests.HTTPError as e:
        return f"HTTP error: {e}"
    except Exception as e:
        return f"Other error: {e}"

    return info

print("正在连接MongoDB")
client = MongoClient("mongodb://localhost:27017/")
db = client["biliStat"]
tb = db['videoInfo']

issue = input('连接正常\n想从第一期爬到多少期？')
issue = int(issue)

for i in range(1, issue + 1):
    infos = launch_page(i)
    tb.insert_many(infos)

# print(tags)

