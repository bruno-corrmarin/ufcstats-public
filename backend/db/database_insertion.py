from dotenv import load_dotenv
import os
import psycopg2
import csv
from bs4 import BeautifulSoup
load_dotenv()

def to_int(value):
    try:
        return int(value) if value and value != "" else None
    except ValueError:
        return None

def connect_db():
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
        # If the connection failed, print an error message and return None
        print("Failed to connect to the database.")
        return None
    
    # create a cursor object to execute SQL commands
    cur = conn.cursor()
    # Truncate the fighters table to remove all existing data before inserting new data from the CSV file
    cur.execute("TRUNCATE TABLE fighters;")
    path = os.path.join(os.path.dirname(__file__), '../scraper/fighterinfo.csv')
    
    # Open the CSV file and read its contents, then insert the data into the fighters table
    with open(path, 'r') as f:
        reader = csv.reader(f)
        for data in reader:
            if len(data) < 11:
                continue
            cur.execute("""
                INSERT INTO fighters (fighter_id, first_name, last_name,
                nickname, height, weight, reach, stance, wins, losses, draws)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (data[0], data[1], data[2], data[3],                    # fighter_id, first_name, last_name, nickname
                to_int(data[4]), to_int(data[5]), to_int(data[6]),      # height, weight, reach
                data[7], to_int(data[8]), to_int(data[9]), to_int(data[10].strip())))  # stance, wins, losses, draws
            conn.commit()
            print("inserted data for fighter_id:", data)
        
    conn.close()



if __name__ == "__main__":
    
    connect_db() 