import requests
from time import sleep
from bs4 import BeautifulSoup


######################################################################
######################################################################
#
#   WebSiteContent class requires URL to initialize an object
#   at initialization class acquires the HTML content of the given URL
#
#   After initialization if needed whole content of the website (other internal webpages)
#   can be fetched with getAllContent()
#
#   To avoid connection rejection from website getAllContent() function waits between
#   every call. For standardization Speed values are introduced
#
#   default is waiting 1s for each call
#
#
#   EXAMPLE
#
#   url = "http://www.test.com"
#   content = WebsiteContent(url)  //content.home_page -> html of the url
#   content.getAllContent(Speed.fast) //content.internal_pages -> [ {<subdomain> : < html of subdomain>}, ...]
#
######################################################################
######################################################################


class Speed:
    insane = 0.01
    fast = 0.1
    normal = 1
    slow = 3
    paranoid = 10


class WebSiteContent:
    def __init__(self, url):
        self.url = url

        if url[0:4] != "http":
            self.url = "http://" + self.url

        try:
            self.home_page = requests.get(self.url).content
        except:
            self.url = "https" + self.url[4:]
            self.home_page = requests.get(self.url).content

        self.internal_pages = []

    def findInternalLinks(self, page_content):
        try:
            soup = BeautifulSoup(page_content, features="html.parser")
            all_links = soup.findAll('a')

            internal_links = []
            for link in all_links:
                try:
                    if link['href'].find(self.url) == 0:
                        internal_links.append(link['href'][len(self.url) - 1:])
                    elif link['href'].find('http') == -1 and link['href'].find('#') == -1 and link['href'] != "/":
                        internal_links.append(link['href'])
                except:
                    pass
            return set(internal_links)
        except:
            return set()

    def getAllContent(self, speed=Speed.normal):
        sleep(speed)

        internal_links = set(self.findInternalLinks(self.home_page))
        used_internal_links = {self.url}

        while len(internal_links) > 0:
            try:
                internal_link = internal_links.pop()
                used_internal_links.add(internal_link)
                print("url:", internal_link, "processing...")

                internal_page = requests.get(self.url[0:-1] + internal_link).content
                internal_links |= set(self.findInternalLinks(internal_page) - used_internal_links)
                self.internal_pages.append({self.url[0:-1] + internal_link: internal_page})
                sleep(speed)
            except requests.exceptions.InvalidURL:
                pass
