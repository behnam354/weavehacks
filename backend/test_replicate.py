#!/usr/bin/env python3
"""
Simple test script to debug Replicate API calls
"""
import os
from dotenv import load_dotenv
import replicate
import time

# Load environment variables from .env file
load_dotenv()

def test_replicate_connection():
    """Test basic Replicate connectivity"""
    print("🔍 Testing Replicate connection...")
    
    # Check API token
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ REPLICATE_API_TOKEN not found in environment")
        return False
    
    print(f"✅ API token found (length: {len(api_token)})")
    
    try:
        # Test client initialization
        print("🔍 Initializing Replicate client...")
        client = replicate.Client(api_token=api_token)
        print("✅ Client initialized successfully")
        
        # Test deployment access
        print("🔍 Testing deployment access...")
        deployment = client.deployments.get("behnam354/qr-code-hackathon")
        print(f"✅ Deployment retrieved: {deployment}")
        
        # Test simple prediction creation (without waiting)
        print("🔍 Testing prediction creation...")
        prediction = deployment.predictions.create(
            input={
                "prompt": "test prompt",
                "seed": 12345,
                "width": 512,
                "height": 512,
                "num_outputs": 1,
            }
        )
        print(f"✅ Prediction created: {prediction.id}")
        print(f"✅ Prediction status: {prediction.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return False

def test_simple_replicate_run():
    """Test using replicate.run() instead of deployment"""
    print("\n🔍 Testing replicate.run() method...")
    
    try:
        output = replicate.run(
            "qr2ai/qr_code_ai_art_generator:3c11545581fedfd84313395213d8805dc23fca60c46f24cd86fb9df407ae7113",
            input={
                "prompt": "simple test",
                "seed": 12345,
                "width": 512,
                "height": 512,
                "num_outputs": 1,
            }
        )
        print(f"✅ replicate.run() succeeded: {output}")
        return True
    except Exception as e:
        print(f"❌ replicate.run() failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Replicate API Test")
    print("=" * 50)
    
    # Test 1: Basic connection
    success1 = test_replicate_connection()
    
    # Test 2: Simple run method
    success2 = test_simple_replicate_run()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.") 