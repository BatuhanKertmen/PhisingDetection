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
WEBSITES_DIR = os.path.join(PYTHON_DIR, "websites")
WEBSITES_CONTENT_DIR = os.path.join(WEBSITES_DIR, "content")
WEBSITES_FEATURE_DIR = os.path.join(WEBSITES_DIR, "feature")
IMAGES_DIR = os.path.join(CRAWLER_DIR, "Images")
FEATURES_DIR = os.path.join(PYTHON_DIR, "Features")


# GO
# GO_DIR = os.path.join(WORKING_DIR, "Go")
# SCRAPED_CONTENT_DIR = os.path.join(GO_DIR, "ScrapedContent")

# -------- FILES ---------- #

# DOMAIN RELATED
VALID_NAMES_TXT = os.path.join(DOMAINS_VALID_DIR, "valid-domain-names.txt")
RAW_NAMES_TXT = os.path.join(DOMAINS_RAW_DIR, "domain-names.txt")
RAW_OPEN_PHISH_TXT = os.path.join(DOMAINS_RAW_DIR, "open_tank_phishing.txt")

# Internal work files
CONTENT_STRUCTURE_JSON = os.path.join(CRAWLER_DIR, "content_structure.json")
REALISTIC_HEADER_JSON = os.path.join(CRAWLER_DIR, "realistic_header.json")
COUNTRY_CODES_TXT = os.path.join(FEATURES_DIR, "country_codes.txt")
TLD_TXT = os.path.join(FEATURES_DIR, "TLD.txt")


def debug():
    print("WORKING_DIR:", WORKING_DIR)
    print("PYTHON_DIR:", PYTHON_DIR)
    print("RAW_DOMAINS_DIR:", DOMAINS_RAW_DIR)
    print("VALID_DOMAINS_DIR:", DOMAINS_VALID_DIR)
    print("CRAWLER_DIR:", CRAWLER_DIR)
    print("IMAGES_DIR:", IMAGES_DIR)
    print("WEBSITES_DIR:", WEBSITES_DIR)
    print("WEBSITES_CONTENT_DIR:", WEBSITES_CONTENT_DIR)
    print("WEBSITES_FEATURE_DIR:", WEBSITES_FEATURE_DIR)
    print("FEATURES_DIR:", FEATURES_DIR)
    print("VALID_NAMES_TXT:", VALID_NAMES_TXT)
    print("RAW_NAMES_TXT:", RAW_NAMES_TXT)
    print("RAW_OPEN_PHISH_TXT:", RAW_OPEN_PHISH_TXT)
    print("CONTENT_STRUCTURE_JSON:", CONTENT_STRUCTURE_JSON)
    print("COUNTRY_CODES_TXT:", COUNTRY_CODES_TXT)
    print("TLD_TXT:", TLD_TXT)
