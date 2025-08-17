#!/usr/bin/env python3
"""
Quick API Test for Phase 4 Server
Tests the API endpoints directly to see what's happening
"""

import requests
import json
import sys

def test_api_endpoints():
    """Test the Phase 4 API endpoints"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Phase 4 API Endpoints...")
    print(f"Base URL: {base_url}")
    
    endpoints = [
        ("/api/status", "System Status"),
        ("/api/models", "Models Info")
    ]
    
    for endpoint, description in endpoints:
        print(f"\n--- Testing {description} ({endpoint}) ---")
        
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"Status Code: {response.status_code}")
            print(f"Content Type: {response.headers.get('Content-Type', 'Unknown')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON Response received ({len(str(data))} chars)")
                    print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                except Exception as e:
                    print(f"❌ Failed to parse JSON: {e}")
                    print(f"Raw response: {response.text[:200]}...")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection failed - Server not running on {base_url}")
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout - Server taking too long to respond")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    # Test main page
    print(f"\n--- Testing Main Page (/) ---")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ Main page loads ({len(response.text)} chars)")
        else:
            print(f"❌ Main page error: {response.status_code}")
    except Exception as e:
        print(f"❌ Main page test failed: {e}")

if __name__ == "__main__":
    print("🚀 Make sure Phase 4 server is running:")
    print("   cd src && python -m main --version phase4")
    print("\nThen run this test in another terminal:")
    print("=" * 50)
    
    test_api_endpoints()
