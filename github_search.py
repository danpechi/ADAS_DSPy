import re
import os
import requests
import json
import base64
from dotenv import load_dotenv
import time
from tqdm import tqdm

def search_code(headers, query, per_page=100, page=1):
    '''
    Function to search for code on GitHub using the GitHub API.
    
    Args: 
        query (str): The search query to be used to search for code.
        per_page (int): The number of results to be fetched per page. Default is 100.
        page (int): The page number of the results to be fetched. Default is 1.

    Returns:
        dict: The JSON response from the GitHub API containing the search results.
    '''

    url = f"https://api.github.com/search/code?q={query}&per_page={per_page}&page={page}"
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.json()}")
        return None

def fetch_all_results(headers, query, per_page=100):
    '''
    Function to fetch all search results across multiple pages.
    
    Args:
        query (str): The search query to be used to search for code.
        per_page (int): The number of results to be fetched per page. Default is 100.
        
    Returns:
        list: A list of dictionaries where each dictionary contains information about a code file.
    '''
    all_results = []
    page = 1
    for _ in range(10): # Run for 10 pages -> 1000 search results
        print(f"Fetching page {page}...")
        time.sleep(1)
        results = search_code(headers, query, per_page=per_page, page=page)
        if results and "items" in results:
            all_results.extend(results["items"])
            if len(results["items"]) < per_page:
                break  # No more results to fetch
            page += 1
        else:
            break
    return all_results

def save_query_results_to_json(headers, query, output_file):
    """
    Fetches results from a query, processes them, and saves them to a JSON file.
    
    Args:
        query (str): The search query to fetch results for.
        output_file (str): The file path to save the results as a JSON file.
    
    Returns:
        str: The path to the saved JSON file.
    """
    all_items = fetch_all_results(headers, query)

    # Process results
    data = [
        {
            "repository": item["repository"]["full_name"],
            "file_name": item["name"],
            "file_path": item["path"],
            "html_url": item["html_url"],
            "download_url": item["url"]
        }
        for item in all_items
    ]

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Results saved to {output_file}")
    return output_file


def main():
    load_dotenv()
    TOKEN = os.getenv('GITHUB_TOKEN')
    HEADERS = {
                "Authorization": f"token {TOKEN}",
                "User-Agent": "DSPY Archiver"
            }
    query = "dspy.Module language:python"
    search_output_file = "script_archive/dspy_code_snippets.json"
    
    save_query_results_to_json(HEADERS, query, search_output_file)  


if __name__ == "__main__":
    main()