import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

def initialize_database(credentials_path):
    """Initialize Firebase and create the initial database structure
    
    Args:
        credentials_path (str): Path to the Firebase credentials JSON file
    """
    try:
        # Initialize Firebase with credentials
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred)
        
        # Get Firestore client
        db = firestore.client()
        
        print("Successfully connected to Firestore!")
        print("Creating initial database structure...")
        
        # Create a test item to ensure the collection exists
        inventory_ref = db.collection('inventory')
        
        # Add a few sample items
        sample_items = [
            {
                'name': 'Laptop',
                'category': 'Electronics',
                'quantity': 10,
                'price': 899.99,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            },
            {
                'name': 'Office Chair',
                'category': 'Furniture',
                'quantity': 5,
                'price': 149.99,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            },
            {
                'name': 'Monitor',
                'category': 'Electronics',
                'quantity': 8,
                'price': 249.99,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
        ]
        
        # Add sample items
        for item in sample_items:
            inventory_ref.add(item)
        
        print(f"Database initialized with {len(sample_items)} sample items!")
        print("You can now run the inventory management system.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")


if __name__ == "__main__":
    # Path to your Firebase credentials file
    creds_path = "inventory-management-sys-ea98a-firebase-adminsdk-fbsvc-b1132ffa2d.json"
    
    # Check if credentials file exists
    if not os.path.exists(creds_path):
        print(f"Error: Firebase credentials file not found at {creds_path}")
        creds_path = input("Enter the path to your Firebase credentials JSON file: ")
        if not os.path.exists(creds_path):
            print("Invalid path. Exiting.")
            exit(1)
    
    # Initialize the database
    initialize_database(creds_path)