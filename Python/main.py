import json
import os

from requests.exceptions import TooManyRedirects, ConnectionError, ReadTimeout

import matplotlib.pyplot as plt
import DownloadDomains
import GetContents
import time
import subprocess  # in order to speed up processes, subprocess module is going to be used
import pathlib
from ping3 import ping
import concurrent.futures
from joblib import Parallel, delayed

import directories as dir

WHO_IS_URL = "https://www.whoisds.com/newly-registered-domains"

zip_link = DownloadDomains.ScrapTodaysDomainsFileLink(WHO_IS_URL)
domains_address = DownloadDomains.DownloadDomainList(zip_link)

domain_file = open(domains_address, 'r')

domain_names = domain_file.readlines()
valid_domain_names = []

def pinging(d_name):
    if ping(d_name[:-1]):
        valid_domain_names.append(d_name[:-1])


tic = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    executor.map(pinging, domain_names[:100])

toc = time.perf_counter()

print('Process finished in {} seconds.'.format(toc - tic))
print("Number of valid domain names is {}".format(len(valid_domain_names)))


def scrape(domain_name, working_directory_path):
    try:
        web = GetContents.WebSiteContent(domain_name)
        web.parseContent()

        file_name = domain_name.replace(".", "-") + ".json"

        path = os.path.join(working_directory_path, "Go", "WebsiteContents", file_name)
        with open(path, "x") as file:
            json.dump(web.parsed_content, file)

        subprocess.Popen("go run " + working_directory_path + "/Go/main.go " + file_name, shell=True)

    except FileExistsError:
        pass
        #print(domain_name, "already exists that's why it is skipped!")
    except ConnectionError:
        pass
        #print("Could not connect to", domain_name, "skipping!")
    except ReadTimeout:
        pass
        #print("Max time exceeded", domain_name, "skipping!")
    except TooManyRedirects:
        pass
        #print(domain_name, "exceeded 30 redirections, skipping!")


resluts = {}
print("----------------------------- BEGINNING --------------------------------------")
try:
    for n_job_count in range(1000, 50001, 250):
        start = time.perf_counter()
        thread = Parallel(n_jobs=n_job_count, prefer="threads")((delayed(scrape)(i, dir.WORKING_DIR) for i in valid_domain_names))
        end = time.perf_counter()
        print(end - start)
        resluts[n_job_count] = end - start
finally:
    x_val = resluts.keys()
    y_val = resluts.values()

    plt.plot(x_val, y_val)
    plt.show()