import csv
import string
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright
import time
import os


# helper function to build urls for each letter in the alphabet to scrape all fighters from the UFC stats website
def url_builder():
    urls = []
    for letter in string.ascii_lowercase:
        urls.append(f"http://ufcstats.com/statistics/fighters?char={letter}&page=all")
    return urls

# writes scraped fighter info to a csv
def scraper(urls):
    # removes old data if it exists to prevent appending to old data
    path = os.path.join(os.path.dirname(__file__), 'fighterinfo.csv') 
    if os.path.exists(path):
        os.remove(path)
    
    # uses playwright to load the page and get the html content, then passes it to the html_processing function
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for url in urls:
            page.goto(url)
            time.sleep(5)
            html_processing(page.content())
            
        browser.close()       
    return

# processes the html content and extracts the relevant data, then writes it to a file
def html_processing(html):
    # parses fighter rows from the html
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.find_all('tr', class_="b-statistics__table-row")
    fighters = []
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3:
            continue

        fighters.append((
            cols[0].find('a'),                    # fighterID (finds html tag 'a' and gets the href attribute, then splits it to get the fighterID)
            clean(cols[0].get_text(strip=True)),  # first name
            clean(cols[1].get_text(strip=True)),  # last name
            clean(cols[2].get_text(strip=True)),  # nickname
            clean(cols[3].get_text(strip=True)),  # height
            clean(cols[4].get_text(strip=True)),  # weight
            clean(cols[5].get_text(strip=True)),  # reach
            clean(cols[6].get_text(strip=True)),  # stance
            clean(cols[7].get_text(strip=True)),  # wins
            clean(cols[8].get_text(strip=True)),  # losses
            clean(cols[9].get_text(strip=True)),  # draws
            ))

    # writes to a csv file
    path = os.path.join(os.path.dirname(__file__), 'fighterinfo.csv')
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for id, firstName, lastName, nickname, height, weight, reach, stance, wins, losses, draws in fighters:
            writer.writerow([
                id['href'].split('/')[-1],  # fighter_id
                clean(firstName),           # first_name
                clean(lastName),            # last_name
                clean(nickname),            # nickname
                clean_height(height),       # height (inches)
                clean_weight(weight),       # weight (lbs)
                clean_reach(reach),         # reach (inches)
                clean(stance),              # stance
                clean(wins),                # wins
                clean(losses),              # losses
                clean(draws)                # draws
            ])
    return 


 # helper functions to clean the data and convert it to the appropriate format for insertion into the database
 
def clean(value):
    return "" if (not value or value == "--") else value

# converts height from feet and inches to inches, returns None if the value is empty or invalid
def clean_height(value):
    parts = value.split("'")
    if len(parts) == 2:
        feet = int(parts[0])
        inches = int(parts[1].replace('"', ''))
        return str(feet * 12 + inches)
    return ""

def clean_weight(value):
    return value.replace(" lbs.", "") if value else ""

def clean_reach(value):
    return value.replace('"', "").strip() if value else ""




# main function to run the scraper and build the urls
if __name__ == "__main__":
    urls = url_builder()
    scraper(urls)