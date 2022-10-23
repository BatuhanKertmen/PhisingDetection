import re
import ssl
import OpenSSL
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from python.utilities.paths import COUNTRY_CODES_TXT


def getDomains(url):
    url_split = url.split("/")[2:-1]
    domain = url_split[0]
    domains_list = domain.split(".")

    last = domains_list[-1]

    with open(COUNTRY_CODES_TXT, "r")as file:
        country_codes = file.read().split("\n")
    tld_idx = -1 if last not in country_codes else -2

    tld = domains_list[tld_idx]
    sub_domains = domains_list[:tld_idx]
    country_code = None if tld_idx == -1 else domains_list[-1]

    return tld, sub_domains, country_code


def getRawDomainName(url):
    tld, subdomains, country_code = getDomains(url)
    if subdomains[0] == "www":
        subdomains = subdomains[1:]

    if country_code:
        raw_domain_name = ".".join(subdomains) + "." + tld + "." + country_code
    else:
        raw_domain_name = ".".join(subdomains) + "." + tld
    return raw_domain_name


def findIfIpBased(url):
    pattern = "[1-9]+[.][1-9]+[.][1-9]+[.][1-9]+"
    search_result = re.search(pattern, url)
    if search_result is not None:
        return True
    return False


def tldPositions(url, tld_list):
    _, sub_domains, _ = getDomains(url)

    tld_indexes = list()
    for sub_domain in sub_domains:
        if sub_domain in tld_list:
            tld_indexes.append(url.find(sub_domain))

    return tld_indexes


def getNumberOfSubDomains(url):
    return len(getDomains(url)[1])


def parseWhoIsRecord(line):
    line_split = line.split(":")
    key = line_split[0]
    value = line_split[1]
    return key.strip(), value.strip()


def getDate(token):
    date_pattern = "[0-9]{4}-[0-9]{2}-[0-9]{2}"
    r = re.search(date_pattern, token)

    if r is None:
        return None
    return r.group()


def getGooglePageRank(url):
    tld, subdomains, _ = getDomains(url)
    if len(subdomains) > 1 and subdomains[0] == "www":
        search_keyword = subdomains[1]
    else:
        search_keyword = subdomains[0]

    received_urls = search(search_keyword, tld=tld, num=100, stop=100, pause=0)
    index = 1
    try:
        for received_url in received_urls:
            if url == received_url:
                return index
            index += 1
    except Exception:
        pass
    return -1


def getCertificateIssuer(domain):
    try:
        cert = ssl.get_server_certificate((domain, 443))
        x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
        return x509.get_issuer().get_components()[1][1].decode("utf-8")
    except Exception:
        return "-"


def downloadWhoisInfo(url):
    domain_name = getRawDomainName(url)
    whois_path = "https://www.whois.com/whois/" + domain_name

    whois_page = requests.get(whois_path).text

    if whois_page.find("Invalid domain name...") != -1:
        return None

    soup = BeautifulSoup(whois_page, features="html.parser")
    raw_data_div = soup.find("div", {"class": "df-block-raw"})

    if raw_data_div is None:
        return []

    return raw_data_div.getText().split("\n")


class Features:
    def __init__(self, url):
        self.url = url
        self.features = {}

    def getFeatures(self):
        return self.features

    def extractAllFeatures(self, tld):
        self.extractUrlBasedFeatures(self.url, tld)
        self.extractLookUpBasedFeatures(self.url)
        self.extractSearchEngineBasedFeatures(self.url)

    def extractUrlBasedFeatures(self, url, tld):
        self.features['isIpBased'] = findIfIpBased(url)
        self.features['numberOfSubDomains'] = getNumberOfSubDomains(url)
        self.features['isContainsAt'] = False if url.find("@") == -1 else True
        self.features['numberOfDashes'] = url.count("-")
        self.features['urlLength'] = len(url)
        self.features['hasEmbeddedDomain'] = (url.count('//') > 1)
        self.features['protocol'] = "https" if url[0:5] == "https" else "http"
        self.features['hasMispositionedTld'] = False if len(tldPositions(url, tld)) == 0 else True

    def extractLookUpBasedFeatures(self, url):
        who_is_info_list = downloadWhoisInfo(url)

        self.features['certificateAuthority'] = getCertificateIssuer(getRawDomainName(url))
        if who_is_info_list is None:
            self.features['whoisMatch'] = False
        else:
            self.features['whoisMatch'] = True
            for item in who_is_info_list:
                if item.find("Creation Date") != -1:
                    self.features['creationDate'] = getDate(parseWhoIsRecord(item)[1])
                elif item.find("Registrant Country") != -1:
                    self.features['country'] = parseWhoIsRecord(item)[1]

    def extractSearchEngineBasedFeatures(self, url):
        self.features['googlePageIndex'] = getGooglePageRank(url)
