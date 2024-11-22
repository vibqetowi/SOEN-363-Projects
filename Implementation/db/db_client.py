import psycopg2
from pprint import pprint

class DatabaseClient:
    def __init__(self, host, database, user, password):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("Connected to database!")
        except Exception as e:
            print("Error connecting to database:", e)
            exit()

    def execute_query(self, query):
        """Executes a given query and prints the result."""
        cur = self.conn.cursor()
        try:
            cur.execute(query)
            if query.strip().upper().startswith('SELECT'):
                # If it's a SELECT query, fetch and pretty print the result
                rows = cur.fetchall()
                print("Query Result:")
                pprint(rows, compact=True)  # Pretty print the rows
            else:
                self.conn.commit()
                print("Query executed successfully.")
        except Exception as e:
            print("Error executing query:", e)
        finally:
            cur.close()

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def create_db(self):
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
            
    def populate_db(self, events):
        cur = self.conn.cursor()

        # Check if Disaster table contains any data
        cur.execute("SELECT COUNT(*) FROM Disaster")
        count = cur.fetchone()[0]

        # If table is not empty, do not populate the database
        if count > 0:
            print("The Disaster table already contains data. Skipping population.")
            cur.close()
            return

        # If the table is empty, proceed with inserting data
        for event in events:
            try:
                # Insert into Disaster table
                disaster_query = """
                    INSERT INTO Disaster (time, type, latitude, longitude)
                    VALUES (%s, %s, %s, %s)
                """
                cur.execute(disaster_query, (event['time'], event['type'], event['latitude'], event['longitude']))

                # Get the last inserted disaster ID
                disaster_id = cur.lastrowid

                # If the event is an earthquake, insert into Earthquake table
                if event['type'].lower() == 'earthquake':
                    earthquake_query = """
                        INSERT INTO Earthquake (disaster_id, depth, magnitude)
                        VALUES (%s, %s, %s)
                    """
                    cur.execute(earthquake_query, (disaster_id, event['depth'], event['magnitude']))

                self.conn.commit()
            except Exception as e:
                print("Error inserting event into database:", e)
                self.conn.rollback()

        cur.close()

    def fetch_disasters(self):
        cur = self.conn.cursor()
        try:
            query = "SELECT * FROM Disaster"
            cur.execute(query)
            disasters = cur.fetchall()
            return disasters
        except Exception as e:
            print("Error fetching disasters:", e)
        finally:
            cur.close()

    def fetch_earthquakes(self):
        cur = self.conn.cursor()
        try:
            query = """
                SELECT D.*, E.depth, E.magnitude
                FROM Disaster D
                INNER JOIN Earthquake E ON D.id = E.disaster_id
            """
            cur.execute(query)
            earthquakes = cur.fetchall()
            return earthquakes
        except Exception as e:
            print("Error fetching earthquakes:", e)
        finally:
            cur.close()

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
