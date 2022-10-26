import json
import multiprocessing
import os
import glob

from ping3 import ping
from itertools import islice
from joblib import Parallel, delayed

from requests.exceptions import TooManyRedirects, ConnectionError, ReadTimeout
from python.download.download_domains import scrapeWhoIsDs
from python.crawlers import get_contents
from python.utilities.paths import VALID_NAMES_TXT, WEBSITES_CONTENT_DIR, WEBSITES_FEATURE_DIR, IMAGES_DIR, TLD_TXT, TRANCO_DOMAINS_TXT
from python.utilities.log import Log
from python.features.featues import Features


os_name = os.name
if not (os_name == "posix" or os_name == "nt"):
    raise OSError("wrong OS")


def pinging(d_name):
    result = ping(d_name)
    if result is not False:
        valid_domain_names.append(d_name)


def scrape(domain_name, folder):
    try:
        web = get_contents.WebSiteContent(domain_name)
        # TODO 
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
    except Exception:
        Log.warning("Unexpected error!")


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


number_of_sites = 5
batch_count = 5
ping_thread_count = 5
scrape_thread_count = 5
feature_thread_count = 5

if __name__ == "__main__":
    #domains_address = scrapeWhoIsDs()
    #domains_address = RAW_NAMES_TXT
    domains_address = TRANCO_DOMAINS_TXT
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

    Log.success("Pinging Done")
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
                    except Exception:
                        pass

                valid_domains.clear()

    Log.success("Scraping Done.")
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
    Log.success("Feature Extraction Done.")
