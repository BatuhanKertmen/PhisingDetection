import json
import os
from requests.exceptions import TooManyRedirects, ConnectionError, ReadTimeout

from Python.Download.DownloadDomains import ScrapeWhoIsDs
import GetContents
import time
import subprocess
from ping3 import ping
from itertools import islice
from joblib import Parallel, delayed
from paths import VALID_NAMES_TXT, WORKING_DIR, RAW_NAMES_TXT


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
        with open(path, "w") as content_file:
            json.dump(web.parsed_content, content_file)

        subprocess.Popen("go run " + str(working_directory_path) + "/Go/main.go " + file_name, shell=True)

    except FileExistsError:
        print(domain_name, "already exists that's why it is skipped!")
    except ConnectionError:
        print("Could not connect to", domain_name, "skipping!")
    except ReadTimeout:
        print("Max time exceeded", domain_name, "skipping!")
    except TooManyRedirects:
        print(domain_name, "exceeded 30 redirections, skipping!")


if __name__ == "__main__":
    domains_address = ScrapeWhoIsDs()
    valid_domain_names = []

    tic = time.perf_counter()
    batch_count = 250
    thread_count = 100
    counter = 0
    with open(domains_address, 'r') as domain_file:
        while True:
            domain_names = list(islice(domain_file, batch_count))

            print("received ", counter * batch_count, "lines")
            if not domain_names:
                break

            Parallel(n_jobs=thread_count, prefer="threads", verbose=10)(delayed(pinging)(i) for i in domain_names)

            print("processed ", counter * batch_count, "lines")

            with open(VALID_NAMES_TXT, "a") as valid_domains_file:
                valid_domains_file.writelines(valid_domain_names)

            print("written to file")

            valid_domain_names.clear()
            counter += 1

    toc = time.perf_counter()
    print('Process finished in {} seconds.'.format(toc - tic))

    batch_count = 250
    thread_count = 100
    try:
        with open(VALID_NAMES_TXT, "r") as file:
            while True:
                valid_domains = list(islice(file, batch_count))
                if not valid_domains:
                    break

                valid_domains = [valid_domain.strip() for valid_domain in valid_domains]
                Parallel(n_jobs=thread_count, prefer="threads", verbose=10)(
                    (delayed(scrape)(i, str(WORKING_DIR)) for i in valid_domains))
    except:
        pass
