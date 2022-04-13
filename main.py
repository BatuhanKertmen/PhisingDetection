# import DownloadDomains
# import GetContents
import time
from ping3 import ping
import concurrent.futures


# WHO_IS_URL = "https://www.whoisds.com/newly-registered-domains"


# zip_link = DownloadDomains.ScrapTodaysDomainsFileLink(WHO_IS_URL)
# DownloadDomains.DownloadDomainList(zip_link)
domain_file = open('./domains/domain-names.txt', 'r')
domain_names = domain_file.readlines()
valid_domain_names = []

def pinging(d_name):
    if ping(d_name[:-1]) != False:
        valid_domain_names.append(d_name[:-1])

tic = time.perf_counter()

with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    executor.map(pinging, domain_names[:1000])

toc = time.perf_counter()

print('Process finished in {} seconds.'.format(toc - tic))
print("Number of valid domain names is {}".format(len(valid_domain_names)))