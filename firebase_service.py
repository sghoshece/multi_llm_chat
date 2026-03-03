"""
Firebase Service Module
Handles Firebase operations for user management and chat history
"""

import os
import json
import uuid
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase (assumes credentials are already set up)
SERVICE_ACCOUNT_KEY = "multi-llm-chat-487904-firebase-adminsdk-fbsvc-014c2efb00.json"

def _ensure_firebase_credentials():
    """Ensure Firebase credentials are available from file or environment variable"""
    global SERVICE_ACCOUNT_KEY
    
    # Check if file exists locally
    if os.path.exists(SERVICE_ACCOUNT_KEY):
        try:
            with open(SERVICE_ACCOUNT_KEY, 'r') as f:
                test_parse = json.load(f)
            print(f"✓ Firebase credentials file found and valid: {SERVICE_ACCOUNT_KEY}")
            return True
        except Exception as e:
            print(f"⚠️  Firebase file exists but is invalid: {e}")
    
    # Try to create from environment variable
    creds_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
    if not creds_json:
        print(f"✗ FIREBASE_SERVICE_ACCOUNT_JSON environment variable not set")
        return False
    
    try:
        print(f"Attempting to parse FIREBASE_SERVICE_ACCOUNT_JSON...")
        
        # Try to parse the JSON
        json_data = json.loads(creds_json)
        print(f"✓ JSON parsed successfully")
        
        # Validate it has required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing = [f for f in required_fields if f not in json_data]
        if missing:
            print(f"⚠️  Missing required fields in JSON: {missing}")
            # Don't fail yet - might still work
        
        # Create file
        print(f"Creating credentials file at {SERVICE_ACCOUNT_KEY}...")
        with open(SERVICE_ACCOUNT_KEY, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Verify it was created and is readable
        if os.path.exists(SERVICE_ACCOUNT_KEY):
            with open(SERVICE_ACCOUNT_KEY, 'r') as f:
                verify = json.load(f)
            print(f"✓ Firebase credentials file created and verified: {SERVICE_ACCOUNT_KEY}")
            return True
        else:
            print(f"✗ File was created but not found when verified")
            return False
            
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in FIREBASE_SERVICE_ACCOUNT_JSON: {e}")
        print(f"   First 100 chars: {creds_json[:100]}")
        return False
    except Exception as e:
        print(f"✗ Error processing Firebase credentials: {e}")
        import traceback
        traceback.print_exc()
        return False


def _get_firestore_client():
    """Get Firestore client, initializing Firebase if needed"""
    if not firebase_admin._apps:
        # Ensure credentials exist
        credentials_ok = _ensure_firebase_credentials()
        
        if not credentials_ok or not os.path.exists(SERVICE_ACCOUNT_KEY):
            error_msg = (
                f"Firebase service account key not found: {SERVICE_ACCOUNT_KEY}\n"
                f"Environment variable FIREBASE_SERVICE_ACCOUNT_JSON may not be set correctly.\n"
                f"The variable should contain the entire JSON from your Firebase service account."
            )
            print(f"✗ {error_msg}")
            raise FileNotFoundError(error_msg)
        
        try:
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
            firebase_admin.initialize_app(cred)
            print(f"✓ Firebase initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing Firebase: {e}")
            raise
    
    return firestore.client()


def get_or_create_google_user(email, display_name=None, picture_url=None, user_id=None):
    """
    Get or create a Google user in Firestore
    
    Args:
        email: User's email
        display_name: User's display name (optional)
        picture_url: User's profile picture URL (optional)
        user_id: User's unique ID (optional, uses email if not provided)
    
    Returns:
        Dictionary containing user data
    """
    try:
        db = _get_firestore_client()
        users_collection = db.collection("users")
        
        # Use email as ID if user_id not provided
        if user_id is None:
            user_id = email
        
        user_ref = users_collection.document(user_id)
        
        # Check if user exists
        doc = user_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        else:
            # Create new user
            user_data = {
                "user_id": user_id,
                "email": email,
                "display_name": display_name or email.split("@")[0],
                "picture_url": picture_url,
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat(),
                "created_timestamp": firestore.SERVER_TIMESTAMP,
            }
            user_ref.set(user_data)
            return user_data
    except Exception as e:
        print(f"Error in get_or_create_google_user: {e}")
        raise


def save_chat_message(user_id, role, content, model=None, conversation_id=None):
    """
    Save a chat message to Firestore
    
    Args:
        user_id: User's ID
        role: Message role ("user" or "assistant")
        content: Message content
        model: Optional LLM model used (e.g., "gemini", "openai")
        conversation_id: Optional conversation ID (creates new if not provided)
    
    Returns:
        Message ID
    """
    try:
        db = _get_firestore_client()
        
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())
        
        message_data = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        
        if model:
            message_data["model"] = model
        
        message_id = str(uuid.uuid4())
        db.collection("messages").document(message_id).set(message_data)
        
        return message_id
    except Exception as e:
        print(f"Error saving chat message: {e}")
        raise


def get_chat_history(user_id, conversation_id=None, limit=50):
    """
    Retrieve chat history for a user
    
    Args:
        user_id: User's ID
        conversation_id: Optional specific conversation ID
        limit: Maximum number of messages to retrieve
    
    Returns:
        List of message dictionaries
    """
    try:
        db = _get_firestore_client()
        query = db.collection("messages").where("user_id", "==", user_id)
        
        if conversation_id:
            query = query.where("conversation_id", "==", conversation_id)
        
        # Note: We don't order in the query to avoid requiring a composite index
        # Instead, we fetch all docs and sort them in Python
        docs = query.stream()
        messages = [doc.to_dict() for doc in docs]
        
        # Sort by created_at timestamp in descending order
        messages.sort(
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )
        
        # Limit results and reverse to get chronological order
        messages = messages[:limit]
        return list(reversed(messages))
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        raise


def clear_chat_history(user_id, conversation_id=None):
    """
    Clear chat history for a user
    
    Args:
        user_id: User's ID
        conversation_id: Optional specific conversation ID (clears all if not provided)
    
    Returns:
        Number of messages deleted
    """
    try:
        db = _get_firestore_client()
        query = db.collection("messages").where("user_id", "==", user_id)
        
        if conversation_id:
            query = query.where("conversation_id", "==", conversation_id)
        
        docs = query.stream()
        deleted_count = 0
        
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1
        
        return deleted_count
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        raise
