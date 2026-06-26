import requests
import json

# Specify the search term
query = "generative ai"

# Define the API endpoint URL for paper relevance search
url = "https://api.semanticscholar.org/graph/v1/paper/search"

# Define the query parameters.
# Unlike bulk search, relevance search uses offset and limit for pagination.
# It can also return more detailed nested information like authors, citations, and references if requested.
query_params = {
    "query": query,
    "fields": "title,year,authors,citationCount", # Requesting some fields
    "limit": 10, # Number of results per page (max 100)
    "offset": 0  # Starting point
}

# Directly define the API key
api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

# Define headers with API key
headers = {"x-api-key": api_key}

print(f"Executing paper relevance search for: '{query}'...")

# Send the API request for the first page
response = requests.get(url, params=query_params, headers=headers).json()

total_results = response.get('total', 0)
print(f"Total matching documents found: {total_results}")

retrieved_papers = []

# Fetch the first two pages (20 results total) as an example
while query_params["offset"] < 20 and "data" in response:
    current_batch = response["data"]
    retrieved_papers.extend(current_batch)
    
    print(f"Retrieved {len(current_batch)} papers at offset {query_params['offset']}...")
    
    # Check if there's a next page indicated by the API
    if "next" not in response:
        break
        
    # Update the offset to the 'next' value provided by the API response for pagination
    query_params["offset"] = response["next"]
    
    # Fetch next page
    response = requests.get(url, params=query_params, headers=headers).json()

# Write the retrieved results to a JSON file
import os
output_file = os.path.join(os.path.dirname(__file__), "relevance_search_results.json")
with open(output_file, "w") as file:
    json.dump(retrieved_papers, file, indent=4)

print(f"\nDone! Retrieved {len(retrieved_papers)} papers and saved to {output_file}.")
