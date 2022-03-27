import DownloadDomains
from ping3 import ping


WHO_IS_URL = "https://www.whoisds.com/newly-registered-domains"

zip_link = DownloadDomains.ScrapTodaysDomainsFileLink(WHO_IS_URL)
print(zip_link)
DownloadDomains.DownloadDomainList(zip_link)


# opening 'domain-names.txt' file and saving it as an object called domain_file
domain_file = open('./domains/domain-names.txt', 'r')

# saving domain names into an array by using the object that we created
# and naming it as domain_names
domain_names = domain_file.readlines()

# storing the valid domain names in an array called valid_domain_names
valid_domain_names = []

# if the domain name is valid, append to the array that we created above
no_domains = 100 # number of domains that we are going to investigate

def isDomainNameValid(domain_name):
  ping_ = ping(domain_name[:-1])
  if ping_ != 0 and ping_ != None:
    valid_domain_names.append(domain_name[:-1])

for domain_name in domain_names[:no_domains]:
  isDomainNameValid(domain_name)
