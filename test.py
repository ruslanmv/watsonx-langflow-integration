import requests

# Replace with your actual Flow UUID
FLOW_ID = "2c02349f-303c-4fbd-b95d-d69646817840"
API_URL = f"http://127.0.0.1:7860/api/v1/run/{FLOW_ID}"

# Input payload for Langflow
payload = {
    "input_value": "hello world!",
    "input_type": "chat",
    "output_type": "chat"
}

headers = {
    "Content-Type": "application/json"
}

try:
    # Send the POST request to Langflow's API
    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()

    # Parse the JSON response
    data = response.json()

    # Attempt to extract the chatbot's response message
    message = (
        data.get("outputs", [{}])[0]
            .get("outputs", [{}])[0]
            .get("results", {})
            .get("message", {})
            .get("text", "")
    )

    if message:
        print("✅ AI Response:")
        print(message)
    else:
        print("⚠️ No valid message found in the response.")
        print("Raw Response:", response.text)

except requests.exceptions.RequestException as e:
    print(f"❌ Network or connection error: {e}")
except ValueError as e:
    print(f"❌ Error decoding JSON: {e}")
