import os
import requests
import json

# Define the API endpoint URL
url = "https://api.semanticscholar.org/graph/v1/author/batch"

# Define the query parameters
query_params = {
    "fields": "name,url,paperCount,hIndex,papers"
}

# Define the request data
data = {
    "ids": ["2281351310", "2281342663", "2300302076", "2300141520"]
}

# Directly define the API key (Reminder: Securely handle API keys in production environments)
api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")  # Using the API key from get_paper_details.py

# Define headers with API key
headers = {"x-api-key": api_key}

# Send the API request
response = requests.post(url, params=query_params, json=data, headers=headers).json()

# Save the results to json file
with open('author_information.json', 'w') as output:
    json.dump(response, output, indent=4)

print(f"Saved author information for {len(response)} authors to author_information.json")
