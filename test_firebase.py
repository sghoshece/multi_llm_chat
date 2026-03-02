"""
Firebase Firestore Integration Test
Tests connection, read, and write operations to the Firebase database
"""

import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Configuration
SERVICE_ACCOUNT_KEY = "multi-llm-chat-487904-firebase-adminsdk-fbsvc-014c2efb00.json"
TEST_COLLECTION = "testing"


def init_firebase():
    """Initialize Firebase with service account credentials"""
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        raise FileNotFoundError(f"Service account key not found: {SERVICE_ACCOUNT_KEY}")
    
    print(f"✓ Found service account key: {SERVICE_ACCOUNT_KEY}")
    
    # Check if Firebase is already initialized
    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
        firebase_admin.initialize_app(cred)
        print("✓ Firebase initialized successfully")
    else:
        print("✓ Firebase already initialized")
    
    return firestore.client()


def test_write_operation(db):
    """Test writing a document to Firestore"""
    print("\n--- Testing Write Operation ---")
    
    test_data = {
        "test_name": "Firebase Integration Test",
        "message": "Hello Firebase!",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data_type": "test"
    }
    
    try:
        # Write a document with auto-generated ID
        doc_ref = db.collection(TEST_COLLECTION).document()
        doc_ref.set(test_data)
        doc_id = doc_ref.id
        
        print(f"✓ Document written successfully!")
        print(f"  Document ID: {doc_id}")
        print(f"  Data: {json.dumps(test_data, indent=2)}")
        
        return doc_id
    except Exception as e:
        print(f"✗ Error writing document: {e}")
        return None


def test_read_operation(db, doc_id):
    """Test reading a document from Firestore"""
    print("\n--- Testing Read Operation ---")
    
    try:
        doc = db.collection(TEST_COLLECTION).document(doc_id).get()
        
        if doc.exists:
            print(f"✓ Document retrieved successfully!")
            print(f"  Document ID: {doc.id}")
            print(f"  Data: {json.dumps(doc.to_dict(), indent=2)}")
            return doc.to_dict()
        else:
            print(f"✗ Document not found: {doc_id}")
            return None
    except Exception as e:
        print(f"✗ Error reading document: {e}")
        return None


def test_query_operation(db):
    """Test querying multiple documents from Firestore"""
    print("\n--- Testing Query Operation ---")
    
    try:
        # Query all documents in the collection
        docs = db.collection(TEST_COLLECTION).limit(5).stream()
        
        doc_count = 0
        for doc in docs:
            doc_count += 1
            if doc_count == 1:
                print(f"✓ Query successful! Found documents:")
            print(f"  - {doc.id}: {doc.to_dict()}")
        
        if doc_count == 0:
            print("⚠ No documents found in collection (this is okay for first test)")
        
        return doc_count
    except Exception as e:
        print(f"✗ Error querying documents: {e}")
        return None


def test_update_operation(db, doc_id):
    """Test updating a document in Firestore"""
    print("\n--- Testing Update Operation ---")
    
    update_data = {
        "status": "updated",
        "updated_at": datetime.now().isoformat(),
        "update_count": firestore.Increment(1)
    }
    
    try:
        db.collection(TEST_COLLECTION).document(doc_id).update(update_data)
        print(f"✓ Document updated successfully!")
        print(f"  Updated fields: {json.dumps(update_data, default=str, indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Error updating document: {e}")
        return False


def test_delete_operation(db, doc_id):
    """Test deleting a document from Firestore"""
    print("\n--- Testing Delete Operation ---")
    
    try:
        db.collection(TEST_COLLECTION).document(doc_id).delete()
        print(f"✓ Document deleted successfully!")
        print(f"  Deleted document ID: {doc_id}")
        return True
    except Exception as e:
        print(f"✗ Error deleting document: {e}")
        return False


def main():
    """Run all Firebase tests"""
    print("=" * 60)
    print("Firebase Firestore Integration Test")
    print("=" * 60)
    
    try:
        # Initialize Firebase
        db = init_firebase()
        print(f"✓ Connected to Firestore collection: '{TEST_COLLECTION}'")
        
        # Run tests
        doc_id = test_write_operation(db)
        
        if doc_id:
            test_read_operation(db, doc_id)
            test_query_operation(db)
            test_update_operation(db, doc_id)
            test_delete_operation(db, doc_id)
            print("\n✓ Attempting to read deleted document (should not exist):")
            test_read_operation(db, doc_id)
        else:
            print("\n✗ Skipping subsequent tests due to write failure")
        
        print("\n" + "=" * 60)
        print("Firebase Integration Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Fatal error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
