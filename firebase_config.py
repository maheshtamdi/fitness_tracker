import firebase_admin
from firebase_admin import credentials, firestore

def initialize_firebase():
    # Initialize the Firebase Admin SDK
    cred = credentials.Certificate("serviceAccountKey.json")  # Your service account key JSON file
    firebase_admin.initialize_app(cred)

    # Get a reference to Firestore
    db = firestore.client()
    return db