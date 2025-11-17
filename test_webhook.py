#!/usr/bin/env python3
"""
Test script for the Status Monitor webhook endpoint.
This script tests various webhook payload formats and the health endpoint.
"""
import json
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on port 8000")
        return False

def test_incident_webhook():
    """Test webhook with incident payload."""
    print("\n🚨 Testing incident webhook...")
    
    payload = {
        "incident": {
            "id": "inc_test_001",
            "name": "OpenAI API - Chat Completions",
            "components": [{"name": "Chat Completions API"}],
            "incident_updates": [
                {
                    "id": "upd_test_001",
                    "created_at": datetime.now().isoformat() + "Z",
                    "body": "We are investigating reports of degraded performance for Chat Completions API"
                }
            ]
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook", json=payload)
        print(f"Incident Webhook Status: {response.status_code}")
        return response.status_code == 204
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on port 8000")
        return False

def test_component_webhook():
    """Test webhook with component payload."""
    print("\n⚙️ Testing component webhook...")
    
    payload = {
        "component": {
            "id": "comp_test_001",
            "name": "GPT-4 API",
            "status": "degraded_performance",
            "updated_at": datetime.now().isoformat() + "Z"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook", json=payload)
        print(f"Component Webhook Status: {response.status_code}")
        return response.status_code == 204
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on port 8000")
        return False

def test_fallback_webhook():
    """Test webhook with unknown payload format."""
    print("\n❓ Testing fallback webhook...")
    
    payload = {
        "message": "Service maintenance scheduled for 2025-11-18 14:00 UTC",
        "service": "OpenAI Platform"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook", json=payload)
        print(f"Fallback Webhook Status: {response.status_code}")
        return response.status_code == 204
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the server is running on port 8000")
        return False

def main():
    """Run all tests."""
    print("🧪 Status Monitor Test Suite")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Incident Webhook", test_incident_webhook),
        ("Component Webhook", test_component_webhook),
        ("Fallback Webhook", test_fallback_webhook),
    ]
    
    results = []
    for name, test_func in tests:
        success = test_func()
        results.append((name, success))
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if not all_passed:
        print("\nMake sure the server is running:")
        print("  C:/Users/saumy/AppData/Local/Programs/Python/Python314/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()