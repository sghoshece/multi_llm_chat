"""
Create a Test Document in Firebase Firestore
Simple script to create a test document in the 'testing' collection
"""

import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Configuration
SERVICE_ACCOUNT_KEY = "multi-llm-chat-487904-firebase-adminsdk-fbsvc-014c2efb00.json"
TEST_COLLECTION = "testing"


def create_test_document():
    """Create a test document in Firestore"""
    
    # Initialize Firebase
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        raise FileNotFoundError(f"Service account key not found: {SERVICE_ACCOUNT_KEY}")
    
    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # Create test document
    test_doc = {
        "name": "Test Document",
        "description": "This is a test document created for Firebase integration verification",
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "test_data": {
            "message": "Firebase write operation successful!",
            "collection": TEST_COLLECTION,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # Write document with specific ID
    doc_id = "test_doc_001"
    
    print("=" * 60)
    print("Creating Test Document in Firebase Firestore")
    print("=" * 60)
    print(f"\nCollection: {TEST_COLLECTION}")
    print(f"Document ID: {doc_id}")
    print(f"\nDocument Data:")
    print(json.dumps(test_doc, indent=2))
    
    try:
        # Set the document
        db.collection(TEST_COLLECTION).document(doc_id).set(test_doc)
        
        # Verify by reading it back
        doc = db.collection(TEST_COLLECTION).document(doc_id).get()
        
        if doc.exists:
            print("\n" + "=" * 60)
            print("✓ Test Document Created Successfully!")
            print("=" * 60)
            print(f"\nVerified Document Data:")
            print(json.dumps(doc.to_dict(), indent=2))
            print(f"\nDocument Path: {TEST_COLLECTION}/{doc_id}")
            return True
        else:
            print("\n✗ Error: Document was not created properly")
            return False
            
    except Exception as e:
        print(f"\n✗ Error creating document: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    create_test_document()
