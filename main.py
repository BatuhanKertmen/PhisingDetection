import json
import multiprocessing
import os
import glob
import time

from ping3 import ping
from itertools import islice
from joblib import Parallel, delayed

from requests.exceptions import TooManyRedirects, ConnectionError
from python.download.download_domains import scrapeWhoIsDs
from python.crawlers import get_contents
from python.utilities.paths import VALID_NAMES_TXT, WEBSITES_CONTENT_DIR, IMAGES_DIR, TRANCO_DOMAINS_TXT, PING_TIMINGS_JSON, SCRAPE_TIMINGS_JSON
from python.utilities.log import Log
from python.utilities.benchmark import Benchmark
from selenium.common.exceptions import TimeoutException

from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

password = os.environ.get('MONGODB_PASSWORD')
connection_string = f"mongodb+srv://d:{password}@cluster.s33rotk.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(connection_string)

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
        web.scrapeUrl()

        file_name = domain_name + ".json"
        path = os.path.join(folder, file_name)
        with open(path, "w") as content_file:
            json.dump(web.parsed_content, content_file)
        links_db = client.links
        def insert_links_doc():
            collection = links_db.link
            link_document = web.parsed_content
            inserted_id = collection.insert_one(link_document).inserted_id
            print(inserted_id)
        insert_links_doc()

    except ConnectionError:
        Log.log("Could not connect to " + domain_name + " skipping!")
    except TimeoutException:
        Log.log("Max time exceeded " + domain_name + " skipping!")
    except TooManyRedirects:
        Log.log(domain_name + " exceeded 30 redirections, skipping!")
    except Exception:
        pass


number_of_sites = 10
batch_count = 10
ping_thread_count = 10
scrape_thread_count = 2

if __name__ == "__main__":
    domains_address = TRANCO_DOMAINS_TXT
    valid_domain_names = []
    counter = 0

    benchmark = Benchmark()
    benchmark.initializeTimer()

    with open(domains_address, 'r') as domain_file:
        with open(VALID_NAMES_TXT, "w") as valid_domains_file:
            while counter < number_of_sites:
                try:
                    domain_names = list(islice(domain_file, batch_count))
                    if not domain_names:
                        break

                    domain_names = [domain_name.strip() for domain_name in domain_names]
                    Parallel(n_jobs=ping_thread_count, prefer="threads", verbose=1)(delayed(pinging)(i) for i in domain_names)
                    valid_domains_file.write('\n'.join(valid_domain_names) + '\n')

                finally:
                    valid_domain_names.clear()
                    counter += batch_count
                    benchmark.record(str(counter) + " domains pinged")


    benchmark.writeRecords(PING_TIMINGS_JSON)
    Log.success("Pinging Done")

    benchmark.reset()
    counter = 0
    with open(VALID_NAMES_TXT, "r") as file:
        while counter < number_of_sites:
            valid_domains = list(islice(file, batch_count))
            if not valid_domains:
                break
            counter += len(valid_domains)
            valid_domains = [valid_domain.strip() for valid_domain in valid_domains]

            try:
                Parallel(n_jobs=scrape_thread_count, prefer="threads", verbose=10)(
                    (delayed(scrape)(i, str(WEBSITES_CONTENT_DIR)) for i in valid_domains))

            except Exception:
                pass

            finally:
                benchmark.record(str(counter) + " many domains scraped")
                files = glob.glob(str(IMAGES_DIR) + "\\*")
                for image_file in files:
                    try:
                        os.remove(image_file)
                    except Exception:
                        pass

                valid_domains.clear()
                time.sleep(3)

    benchmark.writeRecords(SCRAPE_TIMINGS_JSON)
    Log.success("Scraping Done.")
