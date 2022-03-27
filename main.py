import DownloadDomains
import time
import subprocess # in order to speed up processes, subprocess module is going to be used

URL = "https://whoisds.com/newly-registered-domains"

zip_link = DownloadDomains.ScrapTodaysDomainsFileLink(URL)
DownloadDomains.DownloadDomainList(zip_link)

# opening 'domain-names.txt' file and saving it as an object called domain_file
domain_file = open('./domains/domain-names.txt', 'r')

# saving domain names into an array by using the object that we created and naming it as domain_names
domain_names = domain_file.readlines()

# storing the valid domain names in an array called valid_domain_names
valid_domain_names = []

no_domains = 100 # number of domains that we are going to investigate

start_time = time.perf_counter()

results = []

for domain_name in domain_names[:no_domains]:
  process = subprocess.Popen(['ping', '-n', '1',domain_name[:-1]])
  results.append(process)

for d_name, process in zip(domain_names, results):
  if process.wait() == 0:
      valid_domain_names.append(d_name)

end_time = time.perf_counter()

print('Process finished in {} seconds.'.format(end_time - start_time))
print("Number of valid domain names is {}".format(len(valid_domain_names)))