import json
import os

import requests.exceptions

import DownloadDomains
import GetContents
import time
import subprocess  # in order to speed up processes, subprocess module is going to be used
import pathlib
from ping3 import ping
import concurrent.futures


WHO_IS_URL = "https://www.whoisds.com/newly-registered-domains"

zip_link = DownloadDomains.ScrapTodaysDomainsFileLink(WHO_IS_URL)
DownloadDomains.DownloadDomainList(zip_link)

WORKING_DIRECTORY = str(pathlib.Path().resolve())

domain_file = open(WORKING_DIRECTORY + '/Python/domains/domain-names.txt', 'r')

domain_names = domain_file.readlines()[:10]
valid_domain_names = []


def pinging(d_name):
    if ping(d_name[:-1]):
        valid_domain_names.append(d_name[:-1])


tic = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    executor.map(pinging, domain_names[:1000])

toc = time.perf_counter()

print('Process finished in {} seconds.'.format(toc - tic))
print("Number of valid domain names is {}".format(len(valid_domain_names)))


for valid_domain_name in valid_domain_names[:3]:
    try:
        print("--->", valid_domain_name)
        web = GetContents.WebSiteContent(valid_domain_name)
        web.parseContent()

        file_name = valid_domain_name.replace(".", "-") + ".json"

        path = os.path.join(WORKING_DIRECTORY, "Go", "WebsiteContents", file_name)
        with open(path, "x") as file:
            json.dump(web.parsed_content, file)

        subprocess.Popen("go run " + WORKING_DIRECTORY + "/Go/main.go " + file_name, shell=True)

    except FileExistsError:
        print(valid_domain_name, "already exists that's why it is skipped!")
    except requests.exceptions.ConnectionError:
        print("Could not connect to", valid_domain_name, "skipping!")
    except requests.exceptions.ReadTimeout:
        print("Max time exceeded", valid_domain_name, "skipping!")
