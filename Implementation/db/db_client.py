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
        cur = self.conn.cursor()

        # Creating Disaster table (use CREATE TABLE IF NOT EXISTS)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Disaster (
                id SERIAL PRIMARY KEY,
                time TIMESTAMP NOT NULL,
                type VARCHAR(50) NOT NULL,
                latitude NUMERIC(9,6) NOT NULL,
                longitude NUMERIC(9,6) NOT NULL,
                modified_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT chk_coordinates CHECK (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)
            );
            """
        )

        # Creating Earthquake table (use CREATE TABLE IF NOT EXISTS)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Earthquake (
                disaster_id INT PRIMARY KEY,
                depth NUMERIC(5,2) NOT NULL,
                magnitude NUMERIC(3,1) NOT NULL CHECK (magnitude >= 0 AND magnitude <= 10),
                CONSTRAINT fk_earthquake_disaster FOREIGN KEY (disaster_id) REFERENCES Disaster (id) ON DELETE CASCADE
            );
            """
        )

        # Drop the existing trigger if it exists before creating it
        cur.execute(
            """
            DROP TRIGGER IF EXISTS update_takes_modtime ON Disaster;
            """
        )

        # Trigger to update Disaster table
        cur.execute(
            """
            CREATE OR REPLACE FUNCTION update_modified_on()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.modified_on = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER update_takes_modtime
            BEFORE UPDATE ON Disaster
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_on();
            """
        )

        # Drop the existing trigger if it exists before creating it
        cur.execute(
            """
            DROP TRIGGER IF EXISTS earthquake_update_disaster ON Earthquake;
            """
        )

        # Trigger to update corresponding Disaster when changes are made to Earthquake table
        cur.execute(
            """
            CREATE OR REPLACE FUNCTION earthquake_update_disaster()
            RETURNS TRIGGER AS $$
            BEGIN
                UPDATE Disaster
                SET modified_on = NOW()
                WHERE id = NEW.disaster_id;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER earthquake_update_disaster
            AFTER UPDATE ON Earthquake
            FOR EACH ROW
            EXECUTE FUNCTION earthquake_update_disaster();
            """
        )

        self.conn.commit()
        cur.close()

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
