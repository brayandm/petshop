import psycopg2
import os
from dotenv import load_dotenv


# Connect to the database
def connect():
    # Load the variables from the .env file
    load_dotenv()

    # Connect to the database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )

    # Return the cursor (to execute the queries) and the connection (to commit the changes)
    return conn.cursor(), conn
