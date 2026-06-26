import os
import requests
import json

# Set the path parameters
start_release_id = "2023-10-31"
end_release_id = "2023-11-14"
dataset_name = "authors"

# Set the API key. For best practice, store and retrieve API keys via environment variables
api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
headers = {"x-api-key": api_key}

# Construct the complete endpoint URL with the path parameters
url = f"https://api.semanticscholar.org/datasets/v1/diffs/{start_release_id}/to/{end_release_id}/{dataset_name}"

print(f"Fetching incremental diffs for '{dataset_name}' from {start_release_id} to {end_release_id}...")

# Make the API request
response = requests.get(url, headers=headers)

# Extract the diffs from the response
try:
    response_data = response.json()
    if 'diffs' in response_data:
        diffs = response_data['diffs']
        print(f"Found {len(diffs)} diff updates.")
        print(json.dumps(diffs, indent=4))
    else:
        print(f"Response: {response_data}")
except json.JSONDecodeError:
    print(f"Request failed with status {response.status_code}: {response.text}")
