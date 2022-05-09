import requests
from datetime import datetime
from bs4 import BeautifulSoup
from Python.paths import DOMAINS_RAW_DIR

def _calculateTimeDifferenceInMin(time1, time2):
    time1_split = time1.split(':')
    time2_split = time2.split(':')

    time1_min = (int(time1_split[0]) * 60) + int(time1_split[1])
    time2_min = (int(time2_split[0]) * 60) + int(time2_split[1])
    dif = abs(time1_min - time2_min)

    return dif

def scrapeOpenPhising():
    open_tank_url = "https://openphish.com/"
    current_time = datetime.now().strftime("%H:%M:%S")

    open_tank_page = requests.get(open_tank_url)
    soup = BeautifulSoup(open_tank_page.content, features="html.parser")
    domains_table_rows = soup.findAll('tr')

    print("DİR-->", DOMAINS_RAW_DIR)

    with open(DOMAINS_RAW_DIR + "\\open_tank_phishing.txt", "w") as file:
        for domains_table_row in domains_table_rows[1:]:
            upload_time = domains_table_row.contents[5].text
            if _calculateTimeDifferenceInMin(current_time, upload_time) > 240:
                break

            url = domains_table_row.contents[1].text
            file.write(url + "\n")

    return DOMAINS_RAW_DIR + "\\open_tank_phishing.txt"




