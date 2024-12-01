from Implementation.db.export_to_csv import extract_sql_data
from Implementation.firestore_client import migrate_disaster_entitiy, migrate_earthquake_entity
from Implementation.db.db_client import DatabaseClient
from Implementation.config import user, password, host, database


db = DatabaseClient(user=user, password=password, host=host, database=database)
db.connect()

print("Exporting to CSV")
extract_sql_data("./csv_exports", db)

print("Adding disasters to firestore")
migrate_disaster_entitiy()

print("Adding earthquakes to firestore")
migrate_earthquake_entity()

print("Migration finished")