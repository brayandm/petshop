import psycopg2

# Connect to the database
def connect():
    conn = psycopg2.connect()
    return conn.cursor(), conn
