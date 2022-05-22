import re

def _extractUrlFeatures(url):
    at_sign = False
    ip_based = False
    length = len(url)

    if url.find("@") != -1:
        at_sign = True

    pattern = "[1-9]+[.][1-9]+[.][1-9]+[.][1-9]+"
    search_result = re.search(pattern, url)
    if search_result is not None:
        ip_based = True

