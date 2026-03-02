import os
import uuid
import argparse
import time
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

SERVICE_ACCOUNT = "multi-llmproject-ffe3b-firebase-adminsdk-fbsvc-0e993558bd.json"
COLLECTION = "chat"

# Optional OpenAI support
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False


def init_firebase():
    if not os.path.exists(SERVICE_ACCOUNT):
        raise FileNotFoundError(f"Service account JSON not found: {SERVICE_ACCOUNT}")
    cred = credentials.Certificate(SERVICE_ACCOUNT)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    return firestore.client()


def store_message(db, conversation_id, role, text):
    doc = {
        "conversation_id": conversation_id,
        "role": role,
        "text": text,
        "ts": firestore.SERVER_TIMESTAMP,
    }
    ref = db.collection(COLLECTION).document()
    ref.set(doc)
    return ref.id


def generate_reply(user_message):
    # Try to use OpenAI if available and API key set, otherwise echo
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
                messages=[{"role": "user", "content": user_message}]
            )
            # Try to extract text from response in a few common shapes
            content = None
            if hasattr(resp, "choices") and len(resp.choices) > 0:
                choice = resp.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    content = choice.message.content
                elif isinstance(choice, dict) and "message" in choice:
                    content = choice["message"].get("content")
            if content:
                return content
        except Exception:
            pass
    # Fallback simple reply
    return f"Echo: {user_message}"


def interactive_loop(db, conversation_id=None):
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
        print("New conversation id:", conversation_id)
    else:
        print("Using conversation id:", conversation_id)

    print("Enter messages. Type '/quit' to exit.")
    while True:
        try:
            user_msg = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat.")
            break
        if not user_msg:
            continue
        if user_msg.lower() in ("/quit", "/exit"):
            print("Exiting chat.")
            break

        # store user message
        uid = store_message(db, conversation_id, "user", user_msg)
        print(f"Stored user message (doc id: {uid})")

        # generate reply
        reply = generate_reply(user_msg)
        bid = store_message(db, conversation_id, "assistant", reply)
        print(f"Assistant: {reply}  (stored id: {bid})")


def run_test(db):
    # Write a short sample conversation and read it back
    conv_id = str(uuid.uuid4())
    print("Test conversation id:", conv_id)
    u1 = "Hello, this is a test message."
    store_message(db, conv_id, "user", u1)
    r1 = generate_reply(u1)
    store_message(db, conv_id, "assistant", r1)

    # small sleep to allow server timestamp to be set
    time.sleep(1)

    docs = list(db.collection(COLLECTION).where("conversation_id", "==", conv_id).stream())
    print(f"Wrote {len(docs)} documents for test conversation:")
    for d in docs:
        print(d.id, d.to_dict())


def main():
    parser = argparse.ArgumentParser(description="Simple CLI chat that stores messages to Firestore.")
    parser.add_argument("--test", action="store_true", help="Run a short test conversation (non-interactive)")
    parser.add_argument("--conversation-id", type=str, help="Reuse an existing conversation id")
    args = parser.parse_args()

    try:
        db = init_firebase()
    except FileNotFoundError as e:
        print(e)
        return
    except Exception as e:
        print("Failed to initialize Firebase:", e)
        return

    if args.test:
        run_test(db)
    else:
        interactive_loop(db, conversation_id=args.conversation_id)


if __name__ == "__main__":
    main()
