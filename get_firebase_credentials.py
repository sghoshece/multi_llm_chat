#!/usr/bin/env python3
"""
Helper script to extract Firebase service account JSON for Render deployment
"""
import json
import sys

def get_firebase_credentials():
    """Extract Firebase credentials from local file"""
    
    firebase_file = 'multi-llm-chat-487904-firebase-adminsdk-fbsvc-014c2efb00.json'
    
    try:
        with open(firebase_file, 'r') as f:
            creds = json.load(f)
        
        # Print as single-line JSON
        json_str = json.dumps(creds)
        print("\n" + "="*80)
        print("FIREBASE SERVICE ACCOUNT JSON (for Render Environment Variable)")
        print("="*80)
        print("\nCopy the entire text below (including the curly braces):")
        print("\n" + json_str)
        print("\n" + "="*80)
        print("\nSteps to add to Render:")
        print("1. Go to Render Dashboard → multi-llm-chat → Settings")
        print("2. Click Environment Variables")
        print("3. Add new variable:")
        print("   Key: FIREBASE_SERVICE_ACCOUNT_JSON")
        print("   Value: Paste the JSON above (entire thing)")
        print("4. Click Save → Render redeploys automatically")
        print("="*80 + "\n")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: {firebase_file} not found in current directory")
        return False
    except json.JSONDecodeError:
        print(f"Error: {firebase_file} is not valid JSON")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    success = get_firebase_credentials()
    sys.exit(0 if success else 1)
