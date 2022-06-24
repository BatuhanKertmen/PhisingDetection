import json
import multiprocessing
import os
import glob

import urllib3
from ping3 import ping
from itertools import islice
from joblib import Parallel, delayed

from requests.exceptions import TooManyRedirects, ConnectionError, ReadTimeout
from Python.Download.DownloadDomains import ScrapeWhoIsDs
from Python.Crawlers import GetContents
from Python.utilities.paths import VALID_NAMES_TXT, WEBSITES_CONTENT_DIR, WEBSITES_FEATURE_DIR, IMAGES_DIR, TLD_TXT
from Python.utilities.log import Log
from Python.Features.Featues import Features

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def pinging(d_name):
    result = ping(d_name)
    if result is not False:
        valid_domain_names.append(d_name)


def scrape(domain_name, folder):
    try:
        web = GetContents.WebSiteContent(domain_name)
        web.parseContent()

        file_name = domain_name + ".json"
        path = os.path.join(folder, file_name)
        with open(path, "w") as content_file:
            json.dump(web.parsed_content, content_file)

    except ConnectionError:
        Log.log("Could not connect to " + domain_name + " skipping!")
    except ReadTimeout:
        Log.log("Max time exceeded " + domain_name + " skipping!")
    except TooManyRedirects:
        Log.log(domain_name + " exceeded 30 redirections, skipping!")
    except:
        Log.warning("Unexpected error while scraping " + domain_name)

def extractFeatures(filename, tld):
    try:
        with open(filename, "r") as website_content_file:
            website_content = json.load(website_content_file)

        url = website_content['url']
        feat = Features(url)
        feat.extractAllFeatures(tld)

        file_name = filename.split('\\')[-1]
        path = os.path.join(WEBSITES_FEATURE_DIR, file_name)
        with open(path, "w") as content_file:
            json.dump(feat.getFeatures(), content_file)
    except:
        file_name = filename.split('\\')[-1]
        Log.warning("Failed to extract features of " + file_name)



number_of_sites = 250
batch_count = 250
ping_thread_count = 250
scrape_thread_count = 250
feature_thread_count = 250

if __name__ == "__main__":
    domains_address = ScrapeWhoIsDs(check_date=False)

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
                    Parallel(n_jobs=ping_thread_count, prefer="threads", verbose=1)(delayed(pinging)(i) for i in domain_names)
                    valid_domains_file.write('\n'.join(valid_domain_names))

                finally:
                    valid_domain_names.clear()
                    counter += batch_count

    Log.succes("Pinging Done")
    counter = 0
    with open(VALID_NAMES_TXT, "r") as file:
        while counter < number_of_sites:
            valid_domains = list(islice(file, batch_count))
            if not valid_domains:
                break
            counter += len(valid_domains)
            valid_domains = [valid_domain.strip() for valid_domain in valid_domains]

            try:
                Parallel(n_jobs=scrape_thread_count, prefer="threads", verbose=1, timeout=50)(
                    (delayed(scrape)(i, str(WEBSITES_CONTENT_DIR)) for i in valid_domains))

            except multiprocessing.context.TimeoutError:
                pass

            finally:
                files = glob.glob(str(IMAGES_DIR) + "\\*")
                for image_file in files:
                    try:
                        os.remove(image_file)
                    except:
                        pass

                valid_domains.clear()

    Log.succes("Scraping Done.")
    website_files = glob.glob(str(WEBSITES_CONTENT_DIR) + "\\*")

    with open(TLD_TXT, "r") as tld_file:
        tld = tld_file.read().split('\n')

    counter = 0
    while counter < number_of_sites:
        try:
            if counter >= len(website_files):
                break

            remainder = len(website_files) - counter
            batch = batch_count if batch_count < remainder else remainder
            website_contents = website_files[counter: counter + batch]
            website_contents = [website_content.strip() for website_content in website_contents]

            Parallel(n_jobs=feature_thread_count, prefer="threads", verbose=1, timeout=50)(
                delayed(extractFeatures)(i, tld) for i in website_contents)

        except multiprocessing.context.TimeoutError:
            pass

        finally:
            counter += batch_count
    Log.succes("Feature Extraction Done.")


