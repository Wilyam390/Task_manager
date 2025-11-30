#!/usr/bin/env python3
"""
Smoke tests for deployed application
Run these tests after deployment to verify the application is working
"""

import requests
import sys
import json
from time import sleep

def test_health_endpoint(base_url):
    """Test the health check endpoint"""
    print(f"Testing health endpoint: {base_url}/health")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Health check failed with status code: {response.status_code}")
            return False
        
        data = response.json()
        print(f"✅ Health check passed")
        print(f"   Status: {data.get('status')}")
        print(f"   Environment: {data.get('environment')}")
        print(f"   Database: {data.get('database')}")
        print(f"   Task count: {data.get('tasks_count')}")
        return True
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_homepage(base_url):
    """Test the homepage loads"""
    print(f"\nTesting homepage: {base_url}/")
    try:
        response = requests.get(base_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Homepage failed with status code: {response.status_code}")
            return False
        
        if b"Task Manager" not in response.content:
            print(f"❌ Homepage doesn't contain expected content")
            return False
        
        print(f"✅ Homepage loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Homepage error: {e}")
        return False

def test_static_files(base_url):
    """Test that static files are accessible"""
    print(f"\nTesting static files: {base_url}/static/style.css")
    try:
        response = requests.get(f"{base_url}/static/style.css", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Static files not accessible: {response.status_code}")
            return False
        
        print(f"✅ Static files accessible")
        return True
    except Exception as e:
        print(f"❌ Static files error: {e}")
        return False

def run_smoke_tests(base_url):
    """Run all smoke tests"""
    print("=" * 60)
    print("DEPLOYMENT SMOKE TESTS")
    print("=" * 60)
    print(f"Target: {base_url}")
    print("=" * 60)
    
    # Give the app a moment to fully start
    print("\nWaiting 5 seconds for application to warm up...")
    sleep(5)
    
    tests = [
        test_health_endpoint(base_url),
        test_homepage(base_url),
        test_static_files(base_url)
    ]
    
    print("\n" + "=" * 60)
    passed = sum(tests)
    total = len(tests)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("=" * 60)
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smoke_tests.py <base_url>")
        print("Example: python smoke_tests.py https://taskmanager-app.azurewebsites.net")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    exit_code = run_smoke_tests(base_url)
    sys.exit(exit_code)
