"""
Database connection utilities
"""
import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from src.utils.logger import setup_logger

load_dotenv()
logger = setup_logger(__name__)


class DatabaseConnection:
    """PostgreSQL database connection manager"""
    
    def __init__(self):
        self.host = os.getenv("POSTGRES_HOST", "localhost")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.database = os.getenv("POSTGRES_DB", "data_ingestion")
        self.user = os.getenv("POSTGRES_USER", "dataeng")
        self.password = os.getenv("POSTGRES_PASSWORD", "changeme123")
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info(f"Connected to database: {self.database}")
            return self.conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute a query and return results"""
        try:
            self.cursor.execute(query, params)
            # Check if query returns data (SELECT or RETURNING clause)
            if query.strip().upper().startswith("SELECT") or "RETURNING" in query.upper():
                return self.cursor.fetchall()
            else:
                self.conn.commit()
                return self.cursor.rowcount
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def get_db_connection():
    """Get a database connection"""
    return DatabaseConnection()


def init_database():
    """Initialize database with schema (if needed)"""
    logger.info("Initializing database...")
    try:
        with get_db_connection() as db:
            # Check if tables exist
            db.execute_query("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
