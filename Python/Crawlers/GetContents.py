import os
import json
import requests
import pytesseract
pytesseract.pytesseract.tesseract_cmd = os.path.expanduser('~') + r"\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

from PIL import Image
from time import sleep
from bs4 import BeautifulSoup
from Python.paths import CONTENT_STRUCTURE_JSON, REALISTIC_HEADER_JSON, IMAGES_DIR


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
        self.session = requests.Session()

        with open(CONTENT_STRUCTURE_JSON) as content_file:
            self.parsed_content = json.load(content_file)

        with open(REALISTIC_HEADER_JSON) as header_file:
            request_header = json.load(header_file)

        request_header["Host"] = url

        if url[0:4] != "http":
            url = "https://" + url

        response = self.session.get(url, timeout=(2, 10))
        self.url = response.url
        self.home_page = response.text
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
                    byte, width, height, ocr = self.processImage(src)

                    if byte != -1:

                        img = {
                            "src": src,
                            "size": (width, height),
                            "alt": alt,
                            "byte": byte,
                            "ocr": ocr
                        }

                        if self._isSmallestImage(width, height):
                            self.parsed_content['body']['img_smallest'] = img

                        if self._isBiggestImage(width, height):
                            self.parsed_content['body']['img_biggest'] = img

                        self.parsed_content["body"]["img"].append(img)

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

    def processImage(self, image_link):
        image_type = self.getImageType(image_link)
        if image_type == "SKIP":
            return -1, -1, -1, "-1"

        try:
            image_name = IMAGES_DIR + "\\image" + image_type
            image_bytes = self.session.get(image_link).content

            byte = len(image_bytes)

            with open(image_name, 'wb') as handler:
                handler.write(image_bytes)

            with Image.open(image_name) as image:
                width, height = image.size
                ocr_text = pytesseract.image_to_string(image)

            os.remove(image_name)

            return byte, width, height, ocr_text
        except:
            return -1, -1, -1, "-1"

    def _isSmallestImage(self, width, height):
        if self.parsed_content['body']['img_smallest']['size'][0] == 0:
            return True

        small_width = self.parsed_content['body']['img_smallest']['size'][0]
        small_height = self.parsed_content['body']['img_smallest']['size'][1]
        if width * height < small_width * small_height:
            return True

        return False

    def _isBiggestImage(self, width, height):
        if self.parsed_content['body']['img_biggest']['size'][0] == 0:
            return True

        big_width = self.parsed_content['body']['img_biggest']['size'][0]
        big_height = self.parsed_content['body']['img_biggest']['size'][1]
        if width * height > big_width * big_height:
            return True

        return False

    def getImageType(self, image_link):
        if image_link.find(".png") != -1:
            return ".png"
        elif image_link.find(".jpeg") != -1:
            return ".jpeg"
        elif image_link.find(".jpg") != -1:
            return ".jpg"
        elif image_link.find(".apng") != -1:
            return ".apng"
        elif image_link.find(".avif") != -1:
            return ".avif"
        elif image_link.find(".gif") != -1:
            return ".gif"
        elif image_link.find(".jfif") != -1:
            return ".jfif"
        elif image_link.find(".pjpeg") != -1:
            return ".pjpeg"
        elif image_link.find(".pjp") != -1:
            return ".pjp"
        elif image_link.find(".svg") != -1:
            return "SKIP"
        elif image_link.find(".webp") != -1:
            return ".webp"



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

                internal_page = self.session.get(self.url[0:-1] + internal_link).content
                internal_links |= set(self.findInternalLinks(internal_page) - used_internal_links)
                self.internal_pages.append({self.url[0:-1] + internal_link: internal_page})
                sleep(speed)
            except requests.exceptions.InvalidURL:
                pass
