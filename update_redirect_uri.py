#!/usr/bin/env python3
"""
Update redirect_uris in Google Client Secret JSON for Render deployment
Run this after you have your Render URL
"""
import json
import sys

def update_redirect_uri(render_url=None):
    """Update the redirect URIs in the credentials file"""
    
    creds_file = 'client_secret_322929524449-ok5mli1n1o8q049nqm6j7smfklq11g09.apps.googleusercontent.com.json'
    
    try:
        # Read existing credentials
        with open(creds_file, 'r') as f:
            creds = json.load(f)
        
        # Get current redirect URIs
        current_uris = creds.get('web', {}).get('redirect_uris', [])
        print(f"Current redirect URIs: {current_uris}")
        
        if not render_url:
            render_url = input("\nEnter your Render app URL (e.g., https://multi-llm-chat-xxxxx.onrender.com): ").strip()
        
        if not render_url.startswith('http'):
            render_url = 'https://' + render_url
        
        # Ensure it doesn't have a trailing slash
        render_url = render_url.rstrip('/')
        
        # Update redirect URIs - keep localhost for testing, add Render URL
        new_uris = ['http://localhost:8501', render_url]
        
        if 'web' in creds:
            creds['web']['redirect_uris'] = new_uris
        else:
            print("Error: 'web' key not found in credentials JSON")
            return False
        
        # Write back to file
        with open(creds_file, 'w') as f:
            json.dump(creds, f)
        
        print(f"\n✓ Updated redirect URIs to: {new_uris}")
        print(f"\n⚠️  IMPORTANT: Also update these in Google Cloud Console:")
        print(f"   1. Go to Google Cloud Console -> APIs & Services -> Credentials")
        print(f"   2. Edit your OAuth 2.0 Client ID")
        print(f"   3. Update Authorized redirect URIs to:")
        for uri in new_uris:
            print(f"      - {uri}")
        print(f"   4. Save changes")
        
        return True
        
    except FileNotFoundError:
        print(f"Error: {creds_file} not found")
        return False
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {creds_file}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    render_url = sys.argv[1] if len(sys.argv) > 1 else None
    success = update_redirect_uri(render_url)
    sys.exit(0 if success else 1)
