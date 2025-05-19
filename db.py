import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="soundtec_db",
        user="postgres",
        password="admin123",
        host="localhost",
        port="5432"
    )
