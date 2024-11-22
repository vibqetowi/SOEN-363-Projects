from api import gdacs, usgs
from db.db_client import DatabaseClient
from config import user, password, host, database

if __name__ == '__main__':

    # Get the events
    events = []
    events += gdacs.get_events()
    events += usgs.get_events()
    print(events)

    # Establish connection
    db = DatabaseClient(user=user, password=password, host=host, database=database)
    db.connect()
    db.create_db()

    # Populate the db with the events
    db.populate_db(events=events)

    # Executing queries
    # Query 1: Basic SELECT with WHERE
    query1 = "SELECT * FROM Disaster WHERE type = 'Earthquake';"
    db.execute_query(query1)

    # Query 2: Basic SELECT with GROUP BY
    query2 = """
        SELECT type, COUNT(*) AS disaster_count
        FROM Disaster
        GROUP BY type;
        """
    db.execute_query(query2)

    # Query 3: Basic SELECT with GROUP BY and HAVING
    query3 = """
        SELECT type, COUNT(*) AS disaster_count
        FROM Disaster
        GROUP BY type
        HAVING COUNT(*) > 2;
        """
    db.execute_query(query3)

    # Query 4: Simple JOIN Query
    query4 = """
        SELECT D.id, D.type, E.magnitude
        FROM Disaster D
        INNER JOIN Earthquake E ON D.id = E.disaster_id;
        """
    db.execute_query(query4)

    # Query 5: Cartesian Product and WHERE
    query5 = """
        SELECT D.id, D.type, E.magnitude
        FROM Disaster D, Earthquake E
        WHERE D.id = E.disaster_id;
        """
    db.execute_query(query5)

    # Query 6: LEFT OUTER JOIN
    query6 = """
        SELECT D.id, D.type, E.magnitude
        FROM Disaster D
        LEFT JOIN Earthquake E ON D.id = E.disaster_id;
        """
    db.execute_query(query6)

    # Query 7: RIGHT OUTER JOIN
    query7 = """
        SELECT D.id, D.type, E.magnitude
        FROM Disaster D
        RIGHT JOIN Earthquake E ON D.id = E.disaster_id;
        """
    db.execute_query(query7)

    # Query 8: FULL OUTER JOIN
    query8 = """
        SELECT D.id, D.type, E.magnitude
        FROM Disaster D
        FULL OUTER JOIN Earthquake E ON D.id = E.disaster_id;
        """
    db.execute_query(query8)

    # Query 9: Using NULL for Undefined
    query9 = "SELECT * FROM Earthquake WHERE magnitude IS NULL;"
    db.execute_query(query9)

    # Query 10: Use of COALESCE for NULL
    query10 = """
        SELECT disaster_id, COALESCE(magnitude, 0) AS corrected_magnitude
        FROM Earthquake;
        """
    db.execute_query(query10)

    # Query 11: Correlated Query (Find disasters with a magnitude greater than the average for their type)
    query11 = """
        SELECT D.*
        FROM Disaster D
        WHERE EXISTS (
            SELECT 1
            FROM Earthquake E
            WHERE E.disaster_id = D.id AND E.magnitude > (
                SELECT AVG(E2.magnitude)
                FROM Earthquake E2
                WHERE E2.disaster_id = D.id
            )
        );
        """
    db.execute_query(query11)

    # Query 12: INTERSECT
    query12 = """
        SELECT id, type FROM Disaster WHERE type = 'Earthquake'
        INTERSECT
        SELECT id, type FROM Disaster WHERE type = 'Flood';
        """
    db.execute_query(query12)

    # Query 13: UNION
    query13 = """
        SELECT id, type FROM Disaster WHERE type = 'Earthquake'
        UNION
        SELECT id, type FROM Disaster WHERE type = 'Flood';
        """
    db.execute_query(query13)

    # Query 14: EXCEPT
    query14 = """
        SELECT id, type FROM Disaster WHERE type = 'Earthquake'
        EXCEPT
        SELECT id, type FROM Disaster WHERE type = 'Flood';
        """
    db.execute_query(query14)

    # Query 15: View with Hard-Coded Criteria
    query15 = """
        CREATE OR REPLACE VIEW RecentEarthquakes AS
        SELECT *
        FROM Disaster
        WHERE type = 'Earthquake' AND time > '2024-01-01';
        """
    db.execute_query(query15)

    # Query 16: Overlap Constraints
    query16 = """
        SELECT *
        FROM Disaster D1, Disaster D2
        WHERE D1.id <> D2.id AND D1.latitude = D2.latitude AND D1.longitude = D2.longitude;
        """
    db.execute_query(query16)

    # Query 17: Covering Constraints
    query17 = """
        SELECT *
        FROM Disaster D
        WHERE NOT EXISTS (
            SELECT 1
            FROM Earthquake E
            WHERE E.disaster_id = D.id
        );
        """
    db.execute_query(query17)

    # Query 18: Division using NOT IN
    query18 = """
        SELECT D.id
        FROM Disaster D
        WHERE NOT EXISTS (
            SELECT *
            FROM Earthquake E
            WHERE E.disaster_id = D.id
        );
        """
    db.execute_query(query18)

    # Query 19: Division using NOT EXISTS and EXCEPT
    query19 = """
        SELECT D.id
        FROM Disaster D
        WHERE NOT EXISTS (
            SELECT E.disaster_id
            FROM Earthquake E
            WHERE E.disaster_id = D.id
            EXCEPT
            SELECT E2.disaster_id
            FROM Earthquake E2
        );
        """
    db.execute_query(query19)

    # Close the connection after executing all queries
    db.close_connection()