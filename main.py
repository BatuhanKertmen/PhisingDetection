import DownloadDomains

URL = "https://whoisds.com/newly-registered-domains"

zip_link = DownloadDomains.ScrapTodaysDomainsFileLink(URL)
DownloadDomains.DownloadDomainList(zip_link)



