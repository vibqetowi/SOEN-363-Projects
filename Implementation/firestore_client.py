import firebase_admin
from firebase_admin import credentials, firestore
import csv

cred = credentials.Certificate('phase-2-ab6bd-firebase-adminsdk-2wpm3-4ad5c115ea.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def migrate_disaster_entitiy():
    disaster_csv_path = 'csv_exports/disaster.csv'
    with open(disaster_csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            id = row.get("id")
            doc_ref = db.collection('disasters').document(id)
            doc_ref.set(row)
            print(f"Disaster added: {doc_ref.id}")

def migrate_earthquake_entity():
    earthquake_csv_path = 'csv_exports/earthquake.csv'
    with open(earthquake_csv_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            disaster_id = row.get("disaster_id")

            product_ref = db.collection('disasters').document(disaster_id)

            doc_ref = db.collection('earthquakes').document()
            row['disaster_id'] = product_ref
            doc_ref.set(row)

            print(f"Earthquake added: {doc_ref.id}")

