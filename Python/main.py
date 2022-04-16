import json
import os
from itertools import repeat
from requests.exceptions import TooManyRedirects, ConnectionError, ReadTimeout

import matplotlib.pyplot as plt
import DownloadDomains
import GetContents
import time
import subprocess  # in order to speed up processes, subprocess module is going to be used
from ping3 import ping
import concurrent.futures
from joblib import Parallel, delayed
import multiprocessing
from paths import VALID_NAMES_TXT


def pinging(d_name, queue):
    if ping(d_name[:-1]):
        queue.put(d_name)


def writer(dest_filename, some_queue, some_stop_token):
    with open(dest_filename, 'w') as dest_file:
        while True:
            line = some_queue.get()
            if line == some_stop_token:
                return
            dest_file.write(line)


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


if __name__ == "__main__":

    WHO_IS_URL = "https://www.whoisds.com/newly-registered-domains"

    zip_link = DownloadDomains.ScrapTodaysDomainsFileLink(WHO_IS_URL)
    domains_address = DownloadDomains.DownloadDomainList(zip_link)

    domain_file = open(domains_address, 'r')

    domain_names = domain_file.readlines()[:10]

    tic = time.perf_counter()

    queue = multiprocessing.Queue()
    STOP_TOKEN = "STOP!!!"

    writer_process = multiprocessing.Process(target=writer, args=(VALID_NAMES_TXT, queue, STOP_TOKEN))
    writer_process.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
        executor.map(pinging, domain_names[:1000], repeat(queue))

    queue.put(STOP_TOKEN)
    writer_process.join()

    toc = time.perf_counter()

    print('Process finished in {} seconds.'.format(toc - tic))



    results = {}
    print("----------------------------- BENCHMARKING --------------------------------------")

    exit()

    try:
        for n_job_count in range(1000, 50001, 250):
            start = time.perf_counter()
            #thread = Parallel(n_jobs=n_job_count, prefer="threads")((delayed(scrape)(i, str(dir.WORKING_DIR)) for i in valid_domain_names))
            end = time.perf_counter()
            print(end - start)
            results[n_job_count] = end - start
    finally:
        x_val = results.keys()
        y_val = results.values()

        plt.plot(x_val, y_val)
        plt.show()
