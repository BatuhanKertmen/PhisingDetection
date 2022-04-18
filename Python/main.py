import json
import os
from requests.exceptions import TooManyRedirects, ConnectionError, ReadTimeout

import threading
import matplotlib.pyplot as plt
import DownloadDomains
import GetContents
import time
import subprocess  # in order to speed up processes, subprocess module is going to be used
from ping3 import ping
import concurrent.futures
from itertools import islice
from joblib import Parallel, delayed
from paths import VALID_NAMES_TXT, RAW_NAMES_TXT, WORKING_DIR

counter = 1
def pinging(d_name):
    result = ping(d_name[:-1])
    if result is not False:
        print("result:", d_name.strip())
        valid_domain_names.append(d_name)


def scrape(domain_name, working_directory_path):
    try:
        web = GetContents.WebSiteContent(domain_name)
        web.parseContent()

        file_name = domain_name.replace(".", "-") + ".json"

        path = os.path.join(working_directory_path, "Go", "WebsiteContents", file_name)
        with open(path, "w") as file:
            json.dump(web.parsed_content, file)

        subprocess.Popen("go run " + str(working_directory_path) + "/Go/main.go " + file_name, shell=True)

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


download = False
pingit = False
scrap = True

if download:
    WHO_IS_URL = "https://www.whoisds.com/newly-registered-domains"

    zip_link = DownloadDomains.ScrapTodaysDomainsFileLink(WHO_IS_URL)
    domains_address = DownloadDomains.DownloadDomainList(zip_link)
else:
    domains_address = RAW_NAMES_TXT

if pingit:
    valid_domain_names = []

    tic = time.perf_counter()
    batch_count = 200
    thread_count = 50
    counter = 0
    with open(domains_address, 'r') as domain_file:
        while True:
            domain_names = list(islice(domain_file, batch_count))
            print("received ", counter * batch_count, "lines")
            if not domain_names:
                break

            Parallel(n_jobs=thread_count, prefer="threads", verbose=10)(delayed(pinging)(i) for i in domain_names)

            #with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            #    future = executor.map(pinging, domain_names)
            print("processed ", counter * batch_count, "lines")

            with open(VALID_NAMES_TXT, "a") as valid_domains_file:
                valid_domains_file.writelines(valid_domain_names)

            print("written to file")

            valid_domain_names.clear()
            counter += 1

    toc = time.perf_counter()
    print('Process finished in {} seconds.'.format(toc - tic))

if scrap:

    batch_count = 1000

    results = {}
    print("----------------------------- BENCHMARKING --------------------------------------")

    try:
        with open(VALID_NAMES_TXT, "r") as file:
            valid_domains = list(islice(file, batch_count))

        for n_job_count in range(10, 101, 10):
            start = time.perf_counter()
            
            Parallel(n_jobs=n_job_count, prefer="threads", verbose=50)((delayed(scrape)(i.strip(), str(WORKING_DIR)) for i in valid_domains))
            end = time.perf_counter()
            print(end - start)
            results[n_job_count] = end - start

    finally:
        x_val = results.keys()
        y_val = results.values()

        plt.plot(x_val, y_val)
        plt.show()

