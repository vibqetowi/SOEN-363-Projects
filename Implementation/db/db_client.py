import mysql.connector

# host="localhost",
# user="root",
# password="",
# database="363_phase1"

class DatabaseClient:
    def __init__(self, host, database, user, password):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.conn = None

    def connect(self):
        try:
          self.conn = mysql.connector.connect(
              host=self.host,
              database=self.database,
              user=self.user,
              password=self.password
          )
          print("Connected to database!")
        except Exception as e:
          print("Error connecting to database:", e)
          exit()


    def create_db(self):
        def create_table_if_not_exists(query):
            table_name = query.split()[2]

            cur.execute(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s AND table_schema = DATABASE())",
                (table_name,)
            )

            exists = cur.fetchone()[0]
            if not exists:
                cur.execute(query)
                self.conn.commit()

        cur = self.conn.cursor()

        # Creating Disater table
        create_table_if_not_exists(
            """
            CREATE TABLE Disaster (
            id INT AUTO_INCREMENT,
            time DATETIME NOT NULL,
            type VARCHAR(50) NOT NULL,
            latitude DECIMAL(9,6) NOT NULL,
            longitude DECIMAL(9,6) NOT NULL,
            modified_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id, latitude, longitude),
            CONSTRAINT chk_coordinates CHECK (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)
            );
            """
        )

        # Creating Earthquake table
        create_table_if_not_exists(
            """
                CREATE TABLE Earthquake (
                disaster_id INT PRIMARY KEY,
                depth DECIMAL(5,2) NOT NULL,
                magnitude DECIMAL(3,1) NOT NULL CHECK (magnitude >= 0 AND magnitude <= 10),
                CONSTRAINT fk_earthquake_disaster FOREIGN KEY (disaster_id) REFERENCES Disaster (id) ON DELETE CASCADE
            );
                """
        )

        #trigger to update Disaster table
        cur.execute(
            """
            CREATE TRIGGER update_takes_modtime
            BEFORE UPDATE ON Disaster
            FOR EACH ROW
            BEGIN
                SET NEW.modified_on = NOW();
            END
            """
        )

        #trigger to update corresponding Disaster when changes made to Earthquake table
        cur.execute(
            """
            CREATE TRIGGER earthquake_update_disaster
            AFTER UPDATE ON Earthquake
            FOR EACH ROW
            BEGIN
                UPDATE Disaster
                SET modified_on = NOW()
                WHERE id = NEW.disaster_id;
            END
            """
        )

        self.conn.commit()
        cur.close()

    def populate_db(self, events):
        cur = self.conn.cursor()

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
        cur = self.conn.cursor(dictionary=True)
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
        cur = self.conn.cursor(dictionary=True)
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