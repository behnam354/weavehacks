#!/usr/bin/env python3
"""
Check the status of a Replicate prediction
"""
import os
from dotenv import load_dotenv
import replicate

# Load environment variables from .env file
load_dotenv()

def check_prediction(prediction_id):
    """Check the status of a prediction"""
    print(f"🔍 Checking prediction: {prediction_id}")
    
    try:
        client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))
        deployment = client.deployments.get("behnam354/qr-code-hackathon")
        prediction = deployment.predictions.get(prediction_id)
        
        print(f"✅ Prediction status: {prediction.status}")
        print(f"✅ Prediction output: {prediction.output}")
        print(f"✅ Prediction error: {prediction.error}")
        
        return prediction
        
    except Exception as e:
        print(f"❌ Error checking prediction: {e}")
        return None

if __name__ == "__main__":
    # Use the prediction ID from your test
    prediction_id = "skj548d6jhrme0cr0b7b5nt6jm"
    check_prediction(prediction_id) 