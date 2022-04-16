import os
import pathlib

# GENERAL
WORKING_DIR = pathlib.Path().resolve()

# PYTHON
PYTHON_DIR = os.path.join(WORKING_DIR, "Python")
DOMAINS_RAW_DIR = os.path.join(PYTHON_DIR, "domains", "raw")
DOMAINS_VALID_DIR = os.path.join(PYTHON_DIR, "domains", "valid")


# GO
GO_DIR = os.path.join(WORKING_DIR, "Go")
IMAGES_DIR = os.path.join(GO_DIR, "Images")
WEBSITE_CONTENT_DIR = os.path.join(GO_DIR, "WebsiteContents")
SCRAPED_CONTENT_DIR = os.path.join(GO_DIR, "ScrapedContent")


def debug():
    print("WORKING_DIR:", WORKING_DIR)
    print("PYTHON_DIR:", PYTHON_DIR)
    print("RAW_DOMAINS_DIR:", DOMAINS_RAW_DIR)
    print("VALID_DOMAINS_DIR:", DOMAINS_VALID_DIR)
    print("GO_DIR:", GO_DIR)
    print("IMAGES_DIR:", IMAGES_DIR)
    print("WEBSITE_CONTENT_DIR:", WEBSITE_CONTENT_DIR)
    print("SCRAPED_CONTENT_DIR:", SCRAPED_CONTENT_DIR)