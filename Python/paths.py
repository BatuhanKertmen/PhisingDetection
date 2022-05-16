import os
import pathlib

# -------- DIRECTORIES ---------- #

# GENERAL
WORKING_DIR = pathlib.Path().resolve()

# PYTHON
PYTHON_DIR = os.path.join(WORKING_DIR, "Python")
DOMAINS_RAW_DIR = os.path.join(PYTHON_DIR, "domains", "raw")
DOMAINS_VALID_DIR = os.path.join(PYTHON_DIR, "domains", "valid")
CRAWLER_DIR = os.path.join(PYTHON_DIR, "Crawlers")
IMAGES_DIR = os.path.join(CRAWLER_DIR, "Images")


# GO
GO_DIR = os.path.join(WORKING_DIR, "Go")
WEBSITE_CONTENT_DIR = os.path.join(GO_DIR, "WebsiteContents")
SCRAPED_CONTENT_DIR = os.path.join(GO_DIR, "ScrapedContent")


# -------- FILES ---------- #

# DOMAIN RELATED
VALID_NAMES_TXT = os.path.join(DOMAINS_VALID_DIR, "valid-domain-names.txt")
RAW_NAMES_TXT = os.path.join(DOMAINS_RAW_DIR, "domain-names.txt")
RAW_OPEN_PHISH_TXT = os.path.join(DOMAINS_RAW_DIR, "open_tank_phishing.txt")

# Internal work files
CONTENT_STRUCTURE_JSON = os.path.join(CRAWLER_DIR, "content_structure.json")
REALISTIC_HEADER_JSON = os.path.join(CRAWLER_DIR, "realistic_header.json")


def debug():
    print("WORKING_DIR:", WORKING_DIR)
    print("PYTHON_DIR:", PYTHON_DIR)
    print("RAW_DOMAINS_DIR:", DOMAINS_RAW_DIR)
    print("VALID_DOMAINS_DIR:", DOMAINS_VALID_DIR)
    print("CRAWLER_DIR:", CRAWLER_DIR)
    print("GO_DIR:", GO_DIR)
    print("IMAGES_DIR:", IMAGES_DIR)
    print("WEBSITE_CONTENT_DIR:", WEBSITE_CONTENT_DIR)
    print("SCRAPED_CONTENT_DIR:", SCRAPED_CONTENT_DIR)
    print("VALID_NAMES_TXT:", VALID_NAMES_TXT)
    print("RAW_NAMES_TXT:", RAW_NAMES_TXT)
    print("RAW_OPEN_PHISH_TXT:", RAW_OPEN_PHISH_TXT)
    print("CONTENT_STRUCTURE_JSON:", CONTENT_STRUCTURE_JSON)
    print("REALISTIC_HEADER_JSON:", REALISTIC_HEADER_JSON)