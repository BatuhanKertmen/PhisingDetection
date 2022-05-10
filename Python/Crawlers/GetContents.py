import json
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
#   content.parseContent() //parses html of the hom page and stores it in content.parsedContent
#   content.getContent // returns content.parsedContent as a JSON object
#
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
        self.domain = url
        self.url = url
        self.parsed_content = \
            {
                "status_code": None,
                "head":
                    {
                        "title": None,
                        "script": [],
                        "script_count": 0,
                        "link": [],
                        "link_count": 0,
                        "favicon": None,
                        "meta": [],
                        "meta_count": 0
                    },
                "text":
                    {
                        "h1": None,
                        "h2": None,
                        "h3": None,
                        "h4": None,
                        "h5": None,
                        "strong": None,
                        "p": None,
                        "mark": None
                    },
                "body":
                    {
                        "a": [],
                        "img": [],
                        "img_biggest":
                            {
                                "src": None,
                                "size": None,
                                "alt": None,
                                "byte": None
                            },
                        "img_smallest":
                            {
                                "src": None,
                                "size": None,
                                "alt": None,
                                "byte": None
                            },
                        "audio": []
                    }
            }

        with open('realistic_header.json') as json_file:
            header = json.load(json_file)

        if url[0:4] != "http":
            self.url = "https://" + self.url

        try:
            response = requests.get(self.url, headers=header,  timeout=(2, 5))
            self.home_page = response.content
            self.status_code = response.status_code
        except:
            self.url = "http" + self.url[5:]
            header["method"] = "http"
            response = requests.get(self.url, headers=header, timeout=(2, 5))
            self.home_page = response.content
            self.status_code = response.status_code

        self.internal_pages = []

    def getContent(self, indent=2):
        return json.dumps(self.parsed_content, indent=indent)

    def parseContent(self):
        self.parsed_content['status_code'] = self.status_code

        page_soup = BeautifulSoup(self.home_page, features="html.parser")
        self.parseTitle(page_soup.find('title'))
        self.parseScript(page_soup.findAll('script'))
        self.parseLinks(page_soup.findAll('link'))
        self.parseMeta(page_soup.findAll('meta'))
        self.getTextualContent(page_soup)
        self.parseAnchors(page_soup.findAll('a'))
        self.parseImage(page_soup.findAll('img'))
        self.parseAudio(page_soup.findAll('audio'))

    def getTextualContent(self, body):
        text_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'p', 'mark']
        for text_tag in text_tags:
            text_contents = body.findAll(text_tag)

            for text_content in text_contents:
                if self.parsed_content["text"][text_tag]:
                    self.parsed_content["text"][text_tag].append(text_content.text.strip())
                else:
                    self.parsed_content["text"][text_tag] = [text_content.text.strip()]

    def parseScript(self, scripts):
        for script in scripts:
            src = script['src'] if script.has_attr('src') else "local script"

            self.parsed_content["head"]["script"].append(src)


        self.parsed_content["head"]["script_count"] = \
            len(self.parsed_content["head"]["script"]) if self.parsed_content["head"]["script"] else 0

    def parseLinks(self, links):
        for link in links:
            rel = href = None
            if link.has_attr('rel'): rel = link['rel'][0]
            if link.has_attr('href'): href = link['href']

            if rel is not None or href is not None:
                self.parsed_content["head"]["link"].append({"rel": rel, "href": href})

            if rel != -1:
                self.parsed_content['head']['favicon'] = href

        self.parsed_content["head"]["link_count"] = \
            len(self.parsed_content["head"]["link"])


    def parseMeta(self, metas):
        for meta in metas:
            name = content = None
            if meta.has_attr('name'): name = meta['name']
            if meta.has_attr('content'): content = meta['content']

            if name is not None or content is not None:
                self.parsed_content["head"]["meta"].append({"name": name, "content": content})

        self.parsed_content["head"]['meta_count'] = len(self.parsed_content["head"]["meta"])

    def parseTitle(self, title):
        if title is not None:
            self.parsed_content["head"]["title"] = title.text

    def parseAnchors(self, anchors):
        for anchor in anchors:
            href = text = None
            if anchor.has_attr('href'): href = anchor['href']
            if anchor.text: text = anchor.text

            if href is not None or text is not None:
                self.parsed_content["body"]["a"].append(
                    {
                        "href": href,
                        "text": text
                    })

    def parseImage(self, images):
        for image in images:
            if image.has_attr('src'):
                src = self.getImageLink(image)
                if src is not None:
                    alt = image['alt'] if image.has_attr('alt') else None

                    self.parsed_content["body"]["img"].append(
                        {
                            "src": src,
                            "size": (-1, -1),
                            "alt": alt
                        })

    def parseAudio(self, audios):
        for audio in audios:
            src = []
            for child in audio.children:
                if child.name == "source" and child.has_attr('src'):
                    src.append(child['src'])

            self.parsed_content["body"]["audio"].append(
                {
                    "src": src,
                    "auto_play": audio.has_attr("autoplay")
                })


    def getImageLink(self, image):
        if image['src'] == "":
            return None

        url = image['src']
        if url.find('http') == -1:
            if url[0] != "/" and self.url[-1] != "/":
                url = self.url + "/" + url
            else:
                url = self.url + url

        return url

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
