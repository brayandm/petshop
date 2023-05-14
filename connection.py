import psycopg2
import os
import redis
from dotenv import load_dotenv


# Connect to the database
def connect_to_postgres():
    # Load the variables from the .env file
    load_dotenv()

    # Connect to the database
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv('POSTGRES_NAME'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=os.getenv('POSTGRES_PORT')
    )

    # Return the cursor (to execute the queries) and the connection (to commit the changes)
    return conn.cursor(), conn


def connect_to_redis():
    # Load the variables from the .env file
    load_dotenv()

    # Connect to the database
    return redis.Redis(
        host=os.getenv('REDIS_HOST'),
        port=os.getenv('REDIS_PORT'),
        password=os.getenv('REDIS_PASSWORD')
    )