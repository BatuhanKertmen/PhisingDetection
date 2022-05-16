import requests
from Python.paths import CRAWLER_DIR, DOMAINS_RAW_DIR


# Stackoverflow Todd Gamblin
def _find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start


# Stackoverflow Markus Jarderot
# edited by Georgy
def _removeDuplicate(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def scrapeOpenPhishing():
    open_phish_list_url = "https://openphish.com/feed.txt"
    phishing_domains = requests.get(open_phish_list_url).text.split('\n')
    phishing_domains = [line[idx1+1:idx2] for line, idx1, idx2 in
                        [(line.strip(), _find_nth(line.strip(), '/', 2), _find_nth(line.strip(), '/', 3))
                         for line in phishing_domains]]

    with open(CRAWLER_DIR + "\\newly_scraped_domains.txt", "r") as file:
        newly_scraped_domains = [line.strip() for line in file.readlines()]

    unique_phishing_domains = _removeDuplicate(phishing_domains)
    del phishing_domains

    processed_domains = []
    counter = 0
    for domain in unique_phishing_domains:
        if domain in newly_scraped_domains:
            counter += 1
        else:
            processed_domains.append(domain)

        if counter == 5:
            break

    with open(CRAWLER_DIR + "\\newly_scraped_domains.txt", "w") as file:
        file.write('\n'.join(processed_domains[:5]))

    with open(DOMAINS_RAW_DIR + "\\open_tank_phishing.txt", "w") as file:
        file.write('\n'.join(processed_domains))

    return DOMAINS_RAW_DIR + "\\open_tank_phishing.txt"
