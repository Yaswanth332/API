import requests
import json

# Your configuration - EDIT THESE!
BASE_URL = "https://api-jnj7.onrender.com"  # ⬅️ CHANGE THIS
YOUR_TOKEN = "12345-ABCDE"  # ⬅️ CHANGE THIS

print("🚀 Starting API Test...")
print(f"URL: {BASE_URL}")
print(f"Token: {YOUR_TOKEN}")
print("-" * 50)

# Test 1: Health endpoint
print("\n1. Testing /health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Profile endpoint with token
print("\n2. Testing /api/profile with your token...")
try:
    headers = {
        "Authorization": f"Bearer {YOUR_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{BASE_URL}/api/profile", headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Try without token
print("\n3. Testing /api/profile WITHOUT token...")
try:
    response = requests.get(f"{BASE_URL}/api/profile", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 50)
print("📋 Test Complete!")
print("=" * 50)