import json
import os
from itertools import islice
from ping3 import ping

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from utilities.paths import CHROME_DRIVER
from ParsedContent import parsed_content

import GetContents
from concurrent.futures import ThreadPoolExecutor, wait
from utilities.benchmark import Benchmark
from pymongo import MongoClient

password = "kalem123"
connection_string = f"mongodb+srv://d:{password}@cluster.s33rotk.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
links_db = client.links

def pinging(d_name):
    return ping(d_name) is not False


def scrape(driver, url_list):
    for url in url_list:
        if pinging(url):
            try:
                content = parsed_content.copy()
                home_page = GetContents.scrapeUrl(driver, content, url)
                GetContents.parseContent(home_page, content)
                print("------>", url)
                collection = links_db.link
                link_document = content
                inserted_id = collection.insert_one(link_document).inserted_id
            except TimeoutException:
                print("timeout:", url)


thread_count = 8
batch_count = 10

if __name__ == "__main__":

    drivers = list()

    op = Options()
    op.add_argument("--headless")
    op.add_argument("--disable-gpu")
    op.add_argument('--no-sandbox')
    op.add_argument('--disable-dev-shm-usage')

    for i in range(thread_count):
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "eager"
        drivers.append(webdriver.Chrome(CHROME_DRIVER, desired_capabilities=caps, options=op))
        drivers[-1].set_page_load_timeout(30)

    print("drivers opened")

    with open("domain_names.txt", "r") as file:
        valid_domains = list(islice(file, batch_count))
    valid_domains = [valid_domain.strip() for valid_domain in valid_domains]
    print("domains received")

    url_range = len(valid_domains) // thread_count

    futures = list()
    a = Benchmark()
    a.initializeTimer()
    print("running threads")
    with ThreadPoolExecutor(max_workers=thread_count) as executer:
        for idx in range(thread_count):
            futures.append(executer.submit(scrape, drivers[idx], valid_domains[idx * url_range: (idx + 1) * url_range]))
    wait(futures)
    a.writeRecords("times.txt")

    print("closing")
    for driver in drivers:
        driver.quit()

