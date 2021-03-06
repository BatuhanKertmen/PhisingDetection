import os
import zipfile
import requests
from io import BytesIO
from datetime import date
from bs4 import BeautifulSoup
from Python.utilities.log import Log
from Python.utilities.paths import RAW_NAMES_TXT, DOMAINS_RAW_DIR


# returns the
def _ScrapeTodaysDomainsFileLink(check_date):
    WHO_IS_URL = "https://www.whoisds.com/newly-registered-domains"
    whois_page = requests.get(WHO_IS_URL)
    soup = BeautifulSoup(whois_page.content, features="html.parser")
    domains_table_rows = soup.findAll('tr')

    today = date.today().strftime("%Y-%m-%d")
    if check_date:
        if domains_table_rows[1].contents[5].text != today:
            raise Exception("No domain file with the current date!")
    if int(domains_table_rows[1].contents[3].text) <= 0:
        raise Exception("0 domains in the file with the current date")

    return domains_table_rows[1].contents[7].a['href']


# returns address of the downloaded file
def _DownloadDomainList(link):
    try:
        get_zip = requests.get(link)
        zip_file = zipfile.ZipFile(BytesIO(get_zip.content))
        zip_file.extractall(DOMAINS_RAW_DIR)
        Log.succes("Downloading domains successful!")
        return os.path.join(DOMAINS_RAW_DIR, zip_file.namelist()[0])
    except zipfile.BadZipfile:
        Log.warning("Couldn't find zip file! Returning default location")
        return RAW_NAMES_TXT

def ScrapeWhoIsDs(check_date=True):
    zip_link = _ScrapeTodaysDomainsFileLink(check_date)
    file_path = _DownloadDomainList(zip_link)
    return file_path