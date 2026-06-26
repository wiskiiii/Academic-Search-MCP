import os
import requests

base_url = "https://api.semanticscholar.org/datasets/v1/release/"

# This endpoint requires authentication via api key
api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
headers = {"x-api-key": api_key}

# Step 1: See all release dates
print("--- Step 1: Fetching list of releases ---")
response = requests.get(base_url, headers=headers)
releases = response.json()
print(f"Total releases available: {len(releases)}")
print(f"Most recent 5 releases: {releases[-5:]}\n")

# Step 2: See all datasets for a given release date
release_id = "latest"
print(f"--- Step 2: Fetching datasets for release '{release_id}' ---")
response = requests.get(base_url + release_id, headers=headers)
datasets_info = response.json()
datasets = [d['name'] for d in datasets_info.get('datasets', [])]
print(f"Datasets available in this release: {datasets}\n")

# Step 3: Get download links for datasets
dataset_name = 'papers'
print(f"--- Step 3: Fetching download links for dataset '{dataset_name}' ---")
response = requests.get(base_url + release_id + '/dataset/' + dataset_name, headers=headers)
dataset_details = response.json()

print(f"Dataset: {dataset_details.get('name')}")
print(f"Description: {dataset_details.get('description')}")
print(f"Total files: {len(dataset_details.get('files', []))}")
if dataset_details.get('files'):
    print(f"First file link: {dataset_details['files'][0]}")
