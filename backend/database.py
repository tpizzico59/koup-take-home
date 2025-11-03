import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import config


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = psycopg2.connect(config.DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def fetch_one(query, params=None):
    """Execute query and return single row as dict."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return dict(cur.fetchone()) if cur.rowcount > 0 else None


def fetch_all(query, params=None):
    """Execute query and return all rows as list of dicts."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return [dict(row) for row in cur.fetchall()]


def execute_query(query, params=None):
    """Execute query and return affected row count."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.rowcount


def execute_returning(query, params=None):
    """Execute query and return the inserted/updated row."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            return dict(cur.fetchone()) if cur.rowcount > 0 else None