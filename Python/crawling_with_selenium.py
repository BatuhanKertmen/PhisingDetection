# -*- coding: utf-8 -*-
import codecs

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver
import top_one_million_domains

os.environ["PATH"] += os.pathsep + r'C:\Users\Do\geckodriver'
driver = webdriver.Firefox()

for index, website_name in enumerate(top_one_million_domains.domains[:5000]):
    website_index = index
    try:
        driver.get("https://www." + website_name)

        title_of_the_page = ""
        # get the title of the page
        try:
            title_of_the_page = driver.title
        except:
            print("Title does not exist.")

        main_text = ""
        # get the main text if there exists
        try:
            main = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            main_text = main.text
        except:
            print("Main tag does not exist.")

        body_text = ""
        try:
            # get almost eeverything from the body
            body_text = driver.find_element_by_tag_name("body").get_attribute("innerText")
        except:
            print("Body text does not exist.")

        # make a copy of the current screenshot
        driver.save_screenshot(filename='screenshots/WebsiteScreenShot{}.png'.format(website_index))

        # response of the current website
        request = driver.requests[website_index]
        response = request.response.status_code
        print(response)

        with codecs.open('selenium_crawled_texts/text{}.txt'.format(website_index), 'w', 'utf8') as f:
            f.write(title_of_the_page + " " + main_text + " " + body_text)

        with codecs.open('selenium_crawled_responses/response{}.txt'.format(website_index), 'w', 'utf8') as f:
            f.write(str(response))
    except:
        pass

driver.quit()