from pathlib import Path
import os
from dotenv import load_dotenv
import psycopg2

# Load .secrets from parent directory
secrets_path = Path(__file__).parent.parent / '.secrets'
load_dotenv(secrets_path)

# Get database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def execute_ddl():
    """Execute DDL.sql against the PostgreSQL database"""
    # Get path to DDL.sql
    ddl_path = Path(__file__).parent / 'DDL.sql'
    
    try:
        # Read DDL.sql content
        with open(ddl_path, 'r') as f:
            ddl_content = f.read()
        
        # Connect to the database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        
        # Create a cursor and execute the DDL
        with conn.cursor() as cur:
            print("Executing DDL.sql...")
            cur.execute(ddl_content)
        
        # Commit the changes
        conn.commit()
        print("DDL execution completed successfully")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    execute_ddl()