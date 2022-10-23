import requests
from bs4 import BeautifulSoup
from python.utilities.paths import RAW_NAMES_TXT


def downloadDomains():
    open_fish_url = "https://openphish.com/feed.txt"

    whois_page = requests.get(open_fish_url)
    soup = BeautifulSoup(whois_page.content, features="html.parser")

    file = open(RAW_NAMES_TXT, "w")

    new_domains = soup.text.split("\n")
    total_domains = _appendNewDomains(new_domains)

    file.write("\n".join(total_domains)[1:])

    return RAW_NAMES_TXT


def _appendNewDomains(new_domains):
    file = open(RAW_NAMES_TXT, "r")
    domains_set = set(file.read().split("\n"))
    new_domains_set = set(new_domains)

    new_domains_set.union(domains_set)

    return list(new_domains_set)