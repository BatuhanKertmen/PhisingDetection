import pandas as pd
import concurrent.futures
import requests

df = pd.read_csv('top-1m.csv')
top_one_millions_domains = [website for website in df['Website']]
valid_domain_names = []

def pinging(d_name):
    r = requests.get('http://www.'+d_name)
    if r.status_code == 200:
        valid_domain_names.append(r.url)

with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    executor.map(pinging, top_one_millions_domains[:1000])

print("Number of valid domain names is {}".format(len(valid_domain_names)))