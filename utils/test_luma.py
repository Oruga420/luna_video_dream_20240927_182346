import requests
import json
import time

BASE_URL = "https://api.lumalabs.ai/dream-machine/v1"
GENERATIONS_ENDPOINT = f"{BASE_URL}/generations"

headers = {
    "accept": "application/json",
    "authorization": "Bearer luma-65b63206-c3e5-40c3-942c-00654c884583-339c739d-a55a-41da-8f91-17da8fd049e7",
    "content-type": "application/json"
}

payload = {
    "prompt": "**Video Title: Retro Ride: Mario's 8-bit Adventure Participate in this thrilling adventure and relive the magic of the 8-bit era!",
    "keyframes": {
        "frame0": {
            "type": "image",
            "url": "https://i.ibb.co/k2pZLz6/mario.png"
        }
    }
}

def make_request(url, method="POST", data=None):
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "GET":
            response = requests.get(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print("Response Content:")
        print(response.text)

        response.raise_for_status()  # Raises an HTTPError for bad responses

        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if hasattr(e, 'response'):
            print(f"Error response: {e.response.text}")
        return None

def check_generation_status(generation_id):
    status_url = f"{GENERATIONS_ENDPOINT}/{generation_id}"
    while True:
        response = make_request(status_url, method="GET")
        if response:
            print(f"Current status: {response['state']}")
            if response['state'] == 'completed':
                return response
            elif response['state'] == 'failed':
                print(f"Generation failed. Reason: {response.get('failure_reason', 'Unknown')}")
                return None
        else:
            print("Failed to get status.")
            return None
        time.sleep(10)  # Wait for 10 seconds before checking again

# Make the generation request
print("Making generation request...")
generation_response = make_request(GENERATIONS_ENDPOINT, data=payload)

if generation_response:
    print("Generation request successful:")
    print(json.dumps(generation_response, indent=2))
    
    if 'id' in generation_response:
        generation_id = generation_response['id']
        print(f"\nGeneration ID: {generation_id}")
        print("Waiting for generation to complete...")
        
        final_result = check_generation_status(generation_id)
        
        if final_result:
            print("\nGeneration completed!")
            print("Final result:")
            print(json.dumps(final_result, indent=2))
            if 'assets' in final_result and 'video' in final_result['assets']:
                print(f"\nVideo URL: {final_result['assets']['video']}")
            else:
                print("Video URL not found in the response.")
    else:
        print("Generation ID not found in the initial response.")
else:
    print("Generation request failed.")