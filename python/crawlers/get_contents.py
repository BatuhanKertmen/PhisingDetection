from PIL import Image
from bs4 import BeautifulSoup
from collections import Counter

from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from python.Utilities.paths import CONTENT_STRUCTURE_JSON, IMAGES_DIR, CHROME_DRIVER, CHROME_DRIVER_LINUX

import os
import json
import requests
import googletrans
import pytesseract

pytesseract.pytesseract.tesseract_cmd = os.path.expanduser('~') + r"\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

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


class WebSiteContent:
    def __init__(self, url):
        self.domain = url

        with open(CONTENT_STRUCTURE_JSON) as content_file:
            self.parsed_content = json.load(content_file)

        if url[0:4] != "http":
            url = "http://" + url

        if os.name == "nt":
            self.driver = webdriver.Chrome(CHROME_DRIVER)
        elif os.name == "posix":
            self.driver = webdriver.Chrome(CHROME_DRIVER_LINUX)

        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(expected_conditions.presence_of_all_elements_located)

        self.url = self.driver.current_url
        self.__editUrl()

        request = self.driver.requests[0]
        response = request.response.status_code

        self.parsed_content['status_code'] = response
        self.home_page = self.driver.page_source
        self.internal_pages = []

    def __editUrl(self):
        if self.url.count("/") < 3 and self.url[-1] != "/":
            self.url = self.url + "/"

    def getContent(self, indent=2):
        return json.dumps(self.parsed_content, indent=indent)

    def parseContent(self):
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
        tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'p', 'mark']
        translator = googletrans.Translator(service_urls=['translate.googleapis.com'])
        detected_langs = list()
        for tag in tags:
            text_tags = body.findAll(tag)
            texts = [text_tag.text.strip() for text_tag in text_tags]

            if len(texts) > 0:
                for text in texts:
                    if self.parsed_content["text"]["original"][tag]:
                        self.parsed_content["text"]["original"][tag].append(text)
                    else:
                        self.parsed_content["text"]["original"][tag] = [text]

                translation_objects = translator.translate(text=texts)
                detected_langs.extend([translation_object.src for translation_object in translation_objects])

                translated_texts = [translation_object.text.strip() for translation_object in translation_objects]
                for translated_text in translated_texts:
                    if self.parsed_content["text"]["english"][tag]:
                        self.parsed_content["text"]["english"][tag].append(translated_text.strip())
                    else:
                        self.parsed_content["text"]["english"][tag] = [translated_text.strip()]

        if len(detected_langs) > 0:
            occurrence_count = Counter(detected_langs)
            self.parsed_content["dominant_lang"] = occurrence_count.most_common(1)[0][0]

    def parseScript(self, scripts):
        for script in scripts:
            src = script['src'] if script.has_attr('src') else "local script"

            self.parsed_content["head"]["script"].append(src)

        self.parsed_content["head"]["script_count"] = \
            len(self.parsed_content["head"]["script"]) if self.parsed_content["head"]["script"] else 0

    def parseLinks(self, links):
        for link in links:
            rel = href = None
            if link.has_attr('rel'):
                rel = link['rel'][0]

            if link.has_attr('href'):
                href = link['href']

            if rel is not None or href is not None:
                self.parsed_content["head"]["link"].append({"rel": rel, "href": href})

            if rel != -1:
                self.parsed_content['head']['favicon'] = href

        self.parsed_content["head"]["link_count"] = \
            len(self.parsed_content["head"]["link"])

    def parseMeta(self, metas):
        for meta in metas:
            name = content = None
            if meta.has_attr('name'):
                name = meta['name']

            if meta.has_attr('content'):
                content = meta['content']

            if name is not None or content is not None:
                self.parsed_content["head"]["meta"].append({"name": name, "content": content})

        self.parsed_content["head"]['meta_count'] = len(self.parsed_content["head"]["meta"])

    def parseTitle(self, title):
        if title is not None:
            self.parsed_content["head"]["title"] = title.text

    def parseAnchors(self, anchors):
        for anchor in anchors:
            href = text = None
            if anchor.has_attr('href'):
                href = anchor['href']

            if anchor.text:
                text = anchor.text

            if href is not None or text is not None:
                self.parsed_content["body"]["a"].append(
                    {
                        "href": href,
                        "text": text
                    })

    def parseImage(self, images):
        counter = 0
        for image in images:
            counter += 1
            name = self.domain + "-" + str(counter)
            if image.has_attr('src'):
                src = self.__getImageLink(image)
                if src is not None:
                    alt = image['alt'] if image.has_attr('alt') else None
                    byte, width, height, ocr = self.__processImage(src, name)
                    if byte != -1:

                        img = {
                            "src": src,
                            "size": (width, height),
                            "alt": alt,
                            "byte": byte,
                            "ocr": ocr
                        }

                        if self.__isSmallestImage(width, height):
                            self.parsed_content['body']['img_smallest'] = img

                        if self.__isBiggestImage(width, height):
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

    def __getImageLink(self, image):
        if image['src'] == "":
            return None

        url = image['src']

        if url[0:2] == "//":
            return "http:" + url

        if url.find('http') == -1:
            if url[0] != "/" and self.url[-1] != "/":
                url = self.url + "/" + url
            else:
                url = self.url + url

        return url

    def __processImage(self, image_link, name):
        image_type = self.__getImageType(image_link)
        if image_type == "SKIP":
            return -1, -1, -1, "-1"

        try:
            image_name = IMAGES_DIR + "\\" + name.replace('/', '_').replace("http", "").replace(":", "") + image_type
            image_bytes = requests.get(image_link).content

            byte = len(image_bytes)

            with open(image_name, 'wb') as handler:
                handler.write(image_bytes)

            with Image.open(image_name) as image:
                width, height = image.size
                ocr_text = pytesseract.image_to_string(image)

            os.remove(image_name)

            return byte, width, height, ocr_text
        except Exception:
            return -1, -1, -1, "-1"

    def __isSmallestImage(self, width, height):
        if self.parsed_content['body']['img_smallest']['size'][0] == 0:
            return True

        small_width = self.parsed_content['body']['img_smallest']['size'][0]
        small_height = self.parsed_content['body']['img_smallest']['size'][1]
        if width * height < small_width * small_height:
            return True

        return False

    def __isBiggestImage(self, width, height):
        if self.parsed_content['body']['img_biggest']['size'][0] == 0:
            return True

        big_width = self.parsed_content['body']['img_biggest']['size'][0]
        big_height = self.parsed_content['body']['img_biggest']['size'][1]
        if width * height > big_width * big_height:
            return True

        return False

    @staticmethod
    def __getImageType(image_link):
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
            return "SKIP"

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
                except Exception:
                    pass
            return set(internal_links)
        except Exception:
            return set()