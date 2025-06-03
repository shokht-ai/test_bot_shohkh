import psycopg2
from psycopg2 import pool, OperationalError
from contextlib import contextmanager
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


def get_railway_db_config():
    """Extract and validate Railway database configuration"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("DATABASE_URL environment variable not found!")
        raise ValueError("DATABASE_URL is required for Railway deployment")

    try:
        db_params = urlparse(db_url)
        return {
            "host": db_params.hostname,
            "port": db_params.port,
            "dbname": db_params.path[1:],
            "user": db_params.username,
            "password": db_params.password,
            "sslmode": "require",  # Railway requires SSL
            "connect_timeout": 5  # 5 second connection timeout
        }
    except Exception as e:
        logger.error(f"Error parsing DATABASE_URL: {e}")
        raise


# Railway-specific configuration
DB_CONFIG = get_railway_db_config()


# Connection pool with retry logic
def create_connection_pool():
    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                **DB_CONFIG
            )
            logger.info("Successfully created database connection pool")
            return pool
        except OperationalError as e:
            if attempt == max_retries - 1:
                logger.error("Max retries reached for connection pool creation")
                raise
            logger.warning(f"Connection pool attempt {attempt + 1} failed, retrying...")
            time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Unexpected error creating connection pool: {e}")
            raise


connection_pool = create_connection_pool()


def get_connection():
    """Get a database connection with retry logic"""
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            if connection_pool:
                return connection_pool.getconn()
            return psycopg2.connect(**DB_CONFIG)
        except OperationalError as e:
            if attempt == max_retries - 1:
                logger.error("Max retries reached for database connection")
                raise
            logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
            time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"Unexpected connection error: {e}")
            raise


def release_connection(conn):
    """Release connection back to pool with error handling"""
    try:
        if connection_pool:
            connection_pool.putconn(conn)
        else:
            conn.close()
    except Exception as e:
        logger.error(f"Error releasing connection: {e}")


@contextmanager
def get_cursor():
    """Context manager for database cursor with proper resource cleanup"""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn and 'cur' in locals():
            cur.close()
            release_connection(conn)


def execute_query(query, params=None):
    """Execute a query with error logging"""
    if params is None:
        params = []
    try:
        with get_cursor() as cur:
            cur.execute(query, params)
    except Exception as e:
        logger.error(f"Query execution failed: {e}\nQuery: {query}\nParams: {params}")
        raise


def fetch_all(query, params=None):
    """Fetch all results with error logging"""
    if params is None:
        params = []
    try:
        with get_cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    except Exception as e:
        logger.error(f"Fetch all failed: {e}\nQuery: {query}\nParams: {params}")
        raise


def fetch_one(query, params=None):
    """Fetch single result with error logging"""
    if params is None:
        params = []
    try:
        with get_cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
    except Exception as e:
        logger.error(f"Fetch one failed: {e}\nQuery: {query}\nParams: {params}")
        raise