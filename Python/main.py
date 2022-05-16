import json
import multiprocessing
import os
import time
import subprocess

import urllib3
from ping3 import ping
from itertools import islice
from joblib import Parallel, delayed

from requests.exceptions import TooManyRedirects, ConnectionError, ReadTimeout

from Python.Crawlers import GetContents
from Python.Download.DownloadDomains import ScrapeWhoIsDs
from Python.Download.OpenTank import scrapeOpenPhishing
from paths import VALID_NAMES_TXT, WORKING_DIR, RAW_OPEN_PHISH_TXT

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pinging(d_name):
    result = ping(d_name)
    if result is not False:
        valid_domain_names.append(d_name)


def scrape(domain_name, working_directory_path):
    try:
        web = GetContents.WebSiteContent(domain_name)
        web.parseContent()

        file_name = domain_name.replace(".", "-") + ".json"

        path = os.path.join(working_directory_path, "Go", "WebsiteContents", file_name)
        with open(path, "w") as content_file:
            json.dump(web.parsed_content, content_file)

    except ConnectionError:
        print("Could not connect to", domain_name, "skipping!")
    except ReadTimeout:
        print("Max time exceeded", domain_name, "skipping!")
    except TooManyRedirects:
        print(domain_name, "exceeded 30 redirections, skipping!")


number_of_sites = 1000
batch_count = 250
ping_thread_count = 100
scrape_thread_count = 100

if __name__ == "__main__":
    domains_address = ScrapeWhoIsDs()
    valid_domain_names = []
    counter = 0

    with open(domains_address, 'r') as domain_file:
        with open(VALID_NAMES_TXT, "w") as valid_domains_file:
            while counter < number_of_sites:
                try:
                    domain_names = list(islice(domain_file, batch_count))
                    if not domain_names:
                        break

                    domain_names = [domain_name.strip() for domain_name in domain_names]

                    Parallel(n_jobs=ping_thread_count, prefer="threads", verbose=10)(delayed(pinging)(i) for i in domain_names)

                    valid_domains_file.write('\n'.join(valid_domain_names))

                finally:
                    valid_domain_names.clear()
                    counter += batch_count



    with open(VALID_NAMES_TXT, "r") as file:
        while True:
            valid_domains = list(islice(file, batch_count))
            if not valid_domains:
                break

            valid_domains = [valid_domain.strip() for valid_domain in valid_domains]

            try:
                Parallel(n_jobs=scrape_thread_count, prefer="threads", verbose=10, timeout=20)(
                    (delayed(scrape)(i, str(WORKING_DIR)) for i in valid_domains))
            except multiprocessing.context.TimeoutError:
                pass
            finally:
                valid_domains.clear()


