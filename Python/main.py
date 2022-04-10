import json

import requests.exceptions

import DownloadDomains
import GetContents
import time
import subprocess # in order to speed up processes, subprocess module is going to be used
import pathlib

"""
WHO_IS_URL = "https://www.whoisds.com/newly-registered-domains"

zip_link = DownloadDomains.ScrapTodaysDomainsFileLink(WHO_IS_URL)
DownloadDomains.DownloadDomainList(zip_link)
"""


# opening 'domain-names.txt' file and saving it as an object called domain_file
domain_file = open('Python/domains/domain-names.txt', 'r')

# saving domain names into an array by using the object that we created and naming it as domain_names
domain_names = domain_file.readlines()

# storing the valid domain names in an array called valid_domain_names
valid_domain_names = []

no_domains = 100  # number of domains that we are going to investigate

start_time = time.perf_counter()

results = []

for domain_name in domain_names[510:510+no_domains]:
  process = subprocess.Popen(['ping', '-n', '1',domain_name[:-1]])
  results.append(process)


for d_name, process in zip(domain_names, results):
  if process.wait() == 0:
      valid_domain_names.append(d_name.strip())

end_time = time.perf_counter()

print('Process finished in {} seconds.'.format(end_time - start_time))
print("Number of valid domain names is {}".format(len(valid_domain_names)))

WORKING_DIRECTORY = str(pathlib.Path().resolve().parents[0])
for valid_domain_name in valid_domain_names:
    try:
        print(valid_domain_name, "--->")
        web = GetContents.WebSiteContent(valid_domain_name)
        web.parseContent()

        file_name = valid_domain_name.replace(".", "-") + ".json"

        with open(WORKING_DIRECTORY + "\Go\WebsiteContents\\" + file_name, "x") as file:
            json.dump(web.parsed_content, file)

        start = time.perf_counter()
        subprocess.Popen("go run ../Go/main.go " + file_name, shell=True)
        end = time.perf_counter()
        print("time----> ", end - start)

    except FileExistsError:
        print(valid_domain_name, "already exists that's why it is skipped!")
    except requests.exceptions.ConnectionError:
        print("Could not connect to", valid_domain_name, "skipping!")
    except requests.exceptions.ReadTimeout:
        print("Max time exceeded", valid_domain_name, "skipping!")



