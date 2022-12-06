from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup


def scrapeUrl(driver, parsed_content, domain):
    url = "http://" + domain if domain[0:4] != "http" else domain # NOQA

    try:
        driver.get(url)

        if driver.last_request is None:
            parsed_content["status_code"] = 502
            parsed_content["url"] = url

        else:
            url = driver.execute_script("return document.documentURI")
            url = editUrl(url)
            parsed_content["url"] = url
            home_page = driver.page_source
            try:
                parsed_content["status_code"] = driver.last_request.response.status_code
            except AttributeError:
                parsed_content["status_code"] = None
            finally:
                return home_page

    except FileNotFoundError:
        return None


def editUrl(url):
    query_start = url.find("?")
    return url[:query_start]


def parseContent(home_page, parsed_content):
    page_soup = BeautifulSoup(home_page, features="html.parser")

    parsed_content["head"]["title"] = parseTitle(page_soup.find('title'))
    parsed_content["head"]["script"] = parseScript(page_soup.findAll('script'))
    parsed_content["head"]["link"] = parseLinks(page_soup.findAll('link'))
    parsed_content["head"]["favicon"] = parseFavicon(page_soup.findAll('link'))
    parsed_content["head"]["meta"] = parseMeta(page_soup.findAll('meta'))
    parsed_content["body"]["a"] = parseAnchors(page_soup.findAll('a'))

    parsed_content["text"] = getTextualContent(page_soup)


def parseTitle(title):
    if title is not None:
        return title.text


def parseScript(scripts):
    formatted_script_list = list()
    for script in scripts:
        src = script['src'] if script.has_attr('src') else "local script"
        formatted_script_list.append(src)

    return formatted_script_list


def parseLinks(links):
    formatted_link_list = list()
    for link in links:
        rel = href = None
        if link.has_attr('rel'):
            rel = link['rel'][0]

        if link.has_attr('href'):
            href = link['href']

        if rel is not None or href is not None:
            formatted_link_list.append({"rel": rel, "href": href})

    return formatted_link_list


def parseFavicon(links):
    for link in links:
        rel = href = None
        if link.has_attr('rel'):
            rel = link['rel'][0]

        if link.has_attr('href'):
            href = link['href']

        if rel == "favicon" or rel == "shortcut icon":
            return {"rel": rel, "href": href}
    return None


def parseMeta(metas):
    formatted_meta_list = list()
    for meta in metas:
        name = content = None
        if meta.has_attr('name'):
            name = meta['name']

        if meta.has_attr('content'):
            content = meta['content']

        if name is not None or content is not None:
            formatted_meta_list.append({"name": name, "content": content})

    return formatted_meta_list


def parseAnchors(anchors):
    formatted_anchors_list = list()
    for anchor in anchors:
        href = text = None
        if anchor.has_attr('href'):
            href = anchor['href']

        if anchor.text:
            text = anchor.text

        if href is not None or text is not None:
            formatted_anchors_list.append(
                {
                    "href": href,
                    "text": text
                })

    return formatted_anchors_list


def getTextualContent(body):
    formatted_textual_content = {'h1':[], 'h2':[], 'h3':[], 'h4':[], 'h5':[], 'strong':[], 'p':[], 'mark':[]}
    tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'strong', 'p', 'mark']
    for tag in tags:
        text_tags = body.findAll(tag)
        texts = [text_tag.text.strip() for text_tag in text_tags]

        if len(texts) > 0:
            for text in texts:
                formatted_textual_content[tag].append(text)

    return formatted_textual_content
