import time

import psycopg2
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


load_dotenv()

# connects to the database and retrieves fighter IDs, 
# then builds urls for each fighter and returns a list of urls

def fighter_url_builder():
    
    # Connect to the PostgreSQL database using the connection parameters from environment variables
    conn = psycopg2.connect(host=os.getenv('DB_HOST'),
                            database=os.getenv('DB_NAME'),
                            port=os.getenv('DB_PORT'),
                            user=os.getenv('DB_USER'),
                            password=os.getenv('DB_PASSWORD'))
    
    # Check if the connection was successful
    if conn:
        print("Connected to the database successfully!")
    else:
        print("Failed to connect to the database.")
        return None
     
    # creates cursor to execute sql commands
    cur = conn.cursor()
    
    # retrieves fighter IDs from the fighters table in the database
    cur.execute("SELECT fighter_id FROM fighters;")
    fighter_ids = cur.fetchall()
    conn.close()
    
    fighter_urls = []
    
    for fighter_id in fighter_ids:
        fighter_urls.append("http://ufcstats.com/fighter-details/" + fighter_id[0])
        print("added url for fighter_id:", fighter_id[0])
    
    return fighter_urls

def bout_scraper(urls):
    
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


def html_processing(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr', class_='b-fight-details__ table-row')
    for row in rows:
        print("hello")
        print(row)

    
    
    

def main():
    #fighter_urls = fighter_url_builder()
    bout_scraper(["http://ufcstats.com/fighter-details/01641ba5df0c69b0"])
    return
    
if __name__ == "__main__":
    main()