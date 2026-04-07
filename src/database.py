import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        # We try to get connection details from environment variables
        # If not present, we will log a warning when connecting.
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "postgres")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")
        self.conn = None

    def connect(self):
        if self.conn and not self.conn.closed:
            return True

        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.conn.autocommit = True
            return True
        except Exception as e:
            print(f"ERROR: Could not connect to PostgreSQL database: {e}")
            print("Please check your .env file or environment variables for DB_HOST, DB_NAME, DB_USER, etc.")
            return False

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_db(self):
        """Creates the necessary tables if they don't exist."""
        if not self.connect():
            return

        # Warning: This drops the table. Only do this during initial setup/dev.
        # In production, use migrations.
        # drop_query = "DROP TABLE IF EXISTS avisos;"
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS avisos (
            id SERIAL PRIMARY KEY,
            emisor VARCHAR(255),
            hora_solicitud VARCHAR(50),
            fecha VARCHAR(50),
            hotel VARCHAR(255),
            habitacion VARCHAR(50),
            estado VARCHAR(50),
            paciente VARCHAR(255),
            edad VARCHAR(50),
            historia_medica TEXT,
            nacionalidad VARCHAR(100),
            motivo_urgencia TEXT,
            pagador VARCHAR(100),
            seguro VARCHAR(100),
            touroperador VARCHAR(100),
            hora_aviso VARCHAR(50),
            hora_finalizacion VARCHAR(50),
            medico VARCHAR(255),
            diagnostico TEXT,
            traslado VARCHAR(50),
            tipo_traslado VARCHAR(100),
            hora_ambulancia VARCHAR(50),
            ingreso VARCHAR(50),
            medico_ingreso VARCHAR(255),
            observaciones TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            with self.conn.cursor() as cur:
                # cur.execute(drop_query) # Uncomment if you need to reset schema
                cur.execute(create_table_query)
                
                # Check if columns exist and alter if needed (basic migration for missing columns)
                # For now, we assume clean slate or compatible schema.
                
        except Exception as e:
            print(f"Error initializing database schema: {e}")

    def execute_query(self, query, params=None):
        if not self.connect():
            return None
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if query.strip().upper().startswith("SELECT") or "RETURNING" in query.upper():
                    return cur.fetchall()
                return cur.rowcount
        except Exception as e:
            print(f"Query execution error: {e}")
            return None

# Global instance
db = Database()
