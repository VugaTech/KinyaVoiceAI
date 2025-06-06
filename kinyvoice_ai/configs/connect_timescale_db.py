from kinyvoice_ai.configs import settings
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from kinyvoice_ai.configs.settings import Settings

settings = Settings()

# Create a connection pool
connection_pool = None

def init_db_pool():
    global connection_pool
    try:
        connection_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            host=settings.db_config['host'],
            port=settings.db_config['port'],
            user=settings.db_config['user'],
            password=settings.db_config['password'],
            dbname=settings.db_config['db_name'],
            cursor_factory=RealDictCursor
        )
        print("Database connection pool initialized successfully.")
    except Exception as e:
        print(f"Error initializing database connection pool: {e}")
        raise

def get_db_connection():
    if connection_pool is None:
        init_db_pool()
    try:
        connection = connection_pool.getconn()
        connection.autocommit = True
        return connection
    except Exception as e:
        print(f"Error getting connection from pool: {e}")
        return None

def release_db_connection(connection):
    if connection_pool is not None:
        connection_pool.putconn(connection)

def close_db_pool():
    if connection_pool is not None:
        connection_pool.closeall()
        print("Database connection pool closed.")