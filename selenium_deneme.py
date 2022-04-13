import os;
os.environ["PATH"] += os.pathsep + r'C:\Users\D\geckodriver'

from selenium import webdriver
import time
browser = webdriver.Firefox()
browser.get("https://www.nihanozcan.com")

time.sleep(15)

browser.close()