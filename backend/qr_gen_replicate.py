from crewai.tools import tool
import time

# 1. Create a regular function (no decorators)
def generate_qr_art_func(prompt: str, qr_code_content: str = "behnamshahbazi.com/qrwe") -> str:
    """
    Generates a QR code art image using Replicate based on a text prompt.
    Returns the Replicate image URL (frontend can render this directly).
    Uses the deployment 'behnam354/qr-code-hackathon'.
    """
    import replicate
    import requests
    import os

    try:
        print(f"🎨 [TOOL] Generating QR art with prompt: {prompt}")
        print(f"🎨 [TOOL] Starting Replicate API call...")
        
        replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
        if not replicate_api_token:
            raise ValueError("REPLICATE_API_TOKEN not set in environment")
        
        print(f"🎨 [TOOL] API token found, initializing client...")
        client = replicate.Client(api_token=replicate_api_token)
        
        print(f"🎨 [TOOL] Getting deployment...")
        deployment = client.deployments.get("behnam354/qr-code-hackathon")
        print(f"🎨 [TOOL] Deployment retrieved: {deployment}")
        
        print(f"🎨 [TOOL] Creating prediction...")
        prediction = deployment.predictions.create(
            input={
                "prompt": prompt,
                "seed": -1,
                "width": 768,
                "border": 2,
                "height": 768,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "negative_prompt": "Foreboding mystical, unblended, worst quality, normal quality, low quality, low res, blurry, ugly, disfigured, nsfw, people, animal, character, anime",
                "qr_code_content": qr_code_content,
                "qrcode_background": "white",
                "num_inference_steps": 40,
                "controlnet_conditioning_scale": 1.2
            }
        )
        print(f"🎨 [TOOL] Prediction created: {prediction.id}")
        
        print(f"🎨 [TOOL] Waiting for prediction to complete...")
        start_time = time.time()
        try:
            prediction.wait()  # 1 minute timeout
        except Exception as wait_error:
            print(f"❌ [TOOL] Prediction wait failed: {wait_error}")
            raise
        end_time = time.time()
        print(f"🎨 [TOOL] Prediction completed in {end_time - start_time:.2f} seconds")
        
        output = prediction.output
        print(f"🎨 [TOOL] Replicate output: {output}")
        
        if not output or not isinstance(output, list):
            raise ValueError("No output from Replicate prediction")
        
        image_url = output[0]
        print(f"🎨 [TOOL] Image URL: {image_url}")
        
        # Optionally download and save locally for logging
        try:
            print(f"🎨 [TOOL] Downloading image...")
            image_data = requests.get(image_url, timeout=30).content
            file_path = "qr_code_art.png"
            with open(file_path, "wb") as f:
                f.write(image_data)
            print(f"🎨 [TOOL] Image saved to: {file_path}")
        except Exception as e:
            print(f"⚠️ [TOOL] Could not save image locally: {e}")
        
        return image_url
        
    except Exception as e:
        print(f"❌ [TOOL] Error in generate_qr_art_func: {e}")
        import traceback
        print(f"❌ [TOOL] Full traceback: {traceback.format_exc()}")
        return f"Error generating QR code art: {str(e)}"

# 2. Decorate the function to register as a CrewAI tool
generate_qr_art = tool("QRCodeArtGenerator")(generate_qr_art_func)

# 3. ✅ Test the undecorated function directly
if __name__ == "__main__":
    result = generate_qr_art_func("cute cartoon bee holding a wand and wearing wizard clothing")
    print(result) 