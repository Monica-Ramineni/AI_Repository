#!/usr/bin/env python3
"""
Test script for the Dog API functionality
"""

import requests

def test_dog_api():
    """Test the Dog API endpoints"""
    print("🐕 Testing Dog API functionality...\n")
    
    # Test 1: Get random dog
    print("1. Testing get_random_dog...")
    try:
        response = requests.get("https://dog.ceo/api/breeds/image/random")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                print(f"✅ Success! Random dog image: {data['message']}")
            else:
                print("❌ Failed to get random dog image")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    
    # Test 2: Get dog breeds
    print("2. Testing get_dog_breeds...")
    try:
        response = requests.get("https://dog.ceo/api/breeds/list/all")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                breeds = list(data["message"].keys())
                print(f"✅ Success! Found {len(breeds)} breeds")
                print(f"Sample breeds: {', '.join(breeds[:5])}")
            else:
                print("❌ Failed to get dog breeds")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    
    # Test 3: Get specific breed (golden retriever)
    print("3. Testing get_dog_by_breed (golden retriever)...")
    try:
        response = requests.get("https://dog.ceo/api/breed/golden/images/random")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                print(f"✅ Success! Golden retriever image: {data['message']}")
            else:
                print(f"❌ Failed to get golden retriever image: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()
    
    # Test 4: Get breed info (retriever)
    print("4. Testing get_dog_breed_info (retriever)...")
    try:
        response = requests.get("https://dog.ceo/api/breed/retriever/list")
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                sub_breeds = data["message"]
                if sub_breeds:
                    print(f"✅ Success! Retriever sub-breeds: {', '.join(sub_breeds)}")
                else:
                    print("✅ Success! Retriever has no sub-breeds")
            else:
                print(f"❌ Failed to get retriever info: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n🎉 Dog API testing complete!")

if __name__ == "__main__":
    test_dog_api()
