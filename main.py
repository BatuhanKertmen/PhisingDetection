import zipfile
import pathlib
import requests
from io import BytesIO
from datetime import date
from bs4 import BeautifulSoup


today = date.today().strftime("%Y-%m-%d")
URL = "https://whoisds.com/newly-registered-domains"
CURRENT_PATH = pathlib.Path().resolve()


def ScrapTodaysDomains(soup, today):
    domains_table_rows = soup.findAll('tr')
    if domains_table_rows[1].contents[5].text != today:
        raise Exception("Not updated!")
    if int(domains_table_rows[1].contents[3].text) <= 0:
        raise Exception("0 domains with current date")

    return domains_table_rows[1].contents[7].a['href']


def DownloadDomainList(link):
    try:
        get_zip = requests.get(link)
        zip_file = zipfile.ZipFile(BytesIO(get_zip.content))
        zip_file.extractall(str(CURRENT_PATH) + "/domains")
    except:
        raise Exception("An error occurred while downloading zip file")


whois_page = requests.get(URL)
soup = BeautifulSoup(whois_page.content, features="html.parser")

zip_link = ScrapTodaysDomains(soup, today)
DownloadDomainList(zip_link)



