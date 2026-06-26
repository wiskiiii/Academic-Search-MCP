import os
import requests
import json

# Specify the search term
query = '"generative ai"'

# Define the API endpoint URL
url = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"

# Define the query parameters
query_params = {
    "query": '"generative ai"',
    "fields": "title,url,publicationTypes,publicationDate,openAccessPdf",
    "year": "2023-"
}

# Directly define the API key (Reminder: Securely handle API keys in production environments)
api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")  # Using the API key from get_paper_details.py

# Define headers with API key
headers = {"x-api-key": api_key}

# Send the API request
response = requests.get(url, params=query_params, headers=headers).json()

print(f"Will retrieve an estimated {response.get('total', 0)} documents")
retrieved = 0

# Write results to json file and get next batch of results
with open(f"papers.json", "w") as file: # Overwrite existing file initially
    while True:
        if "data" in response:
            retrieved += len(response["data"])
            print(f"Retrieved {retrieved} papers...")
            for paper in response["data"]:
                print(json.dumps(paper), file=file)
        
        # checks for continuation token to get next batch of results
        if "token" not in response or not response["token"]:
            break
            
        # Add the token to the query parameters and request the next batch
        next_params = query_params.copy()
        next_params["token"] = response["token"]
        response = requests.get(url, params=next_params, headers=headers).json()

print(f"Done! Retrieved {retrieved} papers total")
