import os
import zipfile
import requests
from io import BytesIO
from datetime import date
from bs4 import BeautifulSoup
from paths import DOMAINS_RAW_DIR


def ScrapTodaysDomainsFileLink(URL):
    whois_page = requests.get(URL)
    soup = BeautifulSoup(whois_page.content, features="html.parser")
    domains_table_rows = soup.findAll('tr')

    today = date.today().strftime("%Y-%m-%d")
    if domains_table_rows[1].contents[5].text != today:
        raise Exception("No domain file with the current date!")
    if int(domains_table_rows[1].contents[3].text) <= 0:
        raise Exception("0 domains in the file with the current date")

    return domains_table_rows[1].contents[7].a['href']


# returns address of the downloaded file
def DownloadDomainList(link):
    get_zip = requests.get(link)
    zip_file = zipfile.ZipFile(BytesIO(get_zip.content))
    zip_file.extractall(DOMAINS_RAW_DIR)
    return os.path.join(DOMAINS_RAW_DIR, zip_file.namelist()[0])

