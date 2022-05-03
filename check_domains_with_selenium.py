import os
import pandas as pd
from selenium import webdriver
import time

os.environ["PATH"] += os.pathsep + r'C:\Users\D\geckodriver'

df = pd.read_csv('top-1m.csv')
top_one_millions_domains = [website for website in df['Website']]
valid_domain_names = []

for domain in top_one_millions_domains[:10]:
    browser = webdriver.Firefox()
    browser.get('http://www.'+domain)
    time.sleep(5)
    browser.close()