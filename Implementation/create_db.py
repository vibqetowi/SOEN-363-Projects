import mysql.connector

try:
  conn = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="363_phase1"
  )
  print("Connected to database!")
except Exception as e:
  print("Error connecting to database:", e)
  exit()

cur = conn.cursor()

def create_table_if_not_exists(query):
    table_name = query.split()[2]
    cur.execute(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s AND table_schema = DATABASE())",
        (table_name,)
    )
    exists = cur.fetchone()[0]
    if not exists:
        cur.execute(query)
        conn.commit()

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

conn.commit()

cur.close()
conn.close()

