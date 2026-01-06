"""Test FoodData Central API connection."""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_fooddata_connection():
    """Test connection to FoodData Central API."""
    api_key = os.getenv("USDA_API_KEY")
    
    if not api_key:
        print("❌ Error: USDA_API_KEY not found in environment variables")
        return False
    
    print(f"✓ API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test API connection with a simple query
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": "apple",
        "api_key": api_key,
        "pageSize": 1
    }
    
    try:
        print("\n🔍 Testing connection to FoodData Central...")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_hits = data.get('totalHits', 0)
            foods = data.get('foods', [])
            
            print(f"✅ Connection successful!")
            print(f"   - Total results found: {total_hits}")
            
            if foods:
                food = foods[0]
                print(f"   - Sample food: {food.get('description', 'N/A')}")
                print(f"   - FDC ID: {food.get('fdcId', 'N/A')}")
                print(f"   - Data type: {food.get('dataType', 'N/A')}")
            
            return True
        
        elif response.status_code == 403:
            print(f"❌ Authentication failed (403)")
            print(f"   - The API key may be invalid or expired")
            print(f"   - Response: {response.text}")
            return False
        
        elif response.status_code == 429:
            print(f"⚠️  Rate limit exceeded (429)")
            print(f"   - Too many requests. Please wait and try again.")
            return False
        
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"   - Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - API is not responding")
        return False
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Check your internet connection")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("FoodData Central API Connection Test")
    print("=" * 60)
    
    success = test_fooddata_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ FoodData Central API is ready to use!")
    else:
        print("❌ FoodData Central API connection failed")
        print("\nTroubleshooting:")
        print("1. Check your API key at: https://fdc.nal.usda.gov/api-key-signup.html")
        print("2. Verify the key is correctly set in .env file")
        print("3. Ensure you have internet connection")
    print("=" * 60)
