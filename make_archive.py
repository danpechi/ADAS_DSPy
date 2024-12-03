import re
import requests
import base64
import pandas as pd
import time
from tqdm import tqdm
import yaml

def load_config(config_path):
    '''
    Function to load a YAML configuration file.
    Args:
        config_path (str): The path to the YAML configuration file.
    Returns:
        dict: The configuration settings loaded from the file.
    '''
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)  # Use safe_load to avoid arbitrary code execution
    return config

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
    for _ in range(9): # Run for 9 pages -> 900 search results
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

def convert_to_json(headers, query):
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
    return data

def download_github_file(url, headers):
    '''
    Function to download a file from GitHub.
    Args:
        url (str): The URL of the file to be downloaded.
    Returns:
        dict: The JSON response from the GitHub API containing the file content.
    '''
    
    response = requests.get(url, headers=headers)
    
    
    if response.status_code == 200:
        response_dict = response.json()
        return response_dict
    elif response.status_code == 403:
        print("Rate limit reached (403). Waiting for 30 seconds...")
        time.sleep(30)  # Wait for 30 seconds before retrying
        return download_github_file(url, headers)  # Retry the request
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
        return None
    
def extract_decoded_content(response_json):
    '''
    Function to extract the decoded content from the JSON response.
    
    Args:
        response_json (dict): The JSON response from the GitHub API containing the file content.
    Returns:
        str: The decoded content of the file.
    '''
    encoded_content = response_json.get('content')
    if not encoded_content:
        raise ValueError("The response does not contain 'content'")
    decoded_content = base64.b64decode(encoded_content).decode('utf-8')
    return decoded_content

def find_dspy_modules(code_text):
    '''
    Function to find all classes that inherit from dspy.Module in the given code text.

    Args:
        code_text (str): The text of the code to be searched.
    Returns:
        list: A list of strings where each string is the code for a class that inherits from dspy.Module.   
    '''
    # regex pattern to match classes inheriting from dspy.Modules
    pattern = r'class\s+\w+\s*\(\s*dspy\.Module\s*\):[\s\S]*?(?=\n\s*class\s|\Z)'
    # Find all matches using the regex
    matches = re.findall(pattern, code_text)
    return matches

def extract_dspy_modules(dspy_code_snippets, headers):
    """
    Extracts dspy.Module classes from files listed in a JSON file and saves the results to another JSON file.

    Args:
        input_file (str): Path to the input JSON file containing file metadata.
        output_file (str): Path to save the output JSON file with extracted modules.

    
    Returns:
        str: The path to the saved output JSON file.
    """
    dspy_modules = []

    # Iterate over each file in dspy_code_snippets
    for snippet in tqdm(dspy_code_snippets, desc="Processing files"):
        download_url = snippet["download_url"]
        
        # Download the file content
        time.sleep(1)  # Avoid overloading the server
        file_data = download_github_file(download_url, headers)
        if file_data:
            # Decode the content of the file
            code_text = extract_decoded_content(file_data)
            
            # Find all dspy.Module classes in the code
            modules = find_dspy_modules(code_text)
            
            if modules:
                # Save file info and found modules
                dspy_modules.append({
                    "repository": snippet["repository"],
                    "file_name": snippet["file_name"],
                    "file_path": snippet["file_path"],
                    "html_url": snippet["html_url"],
                    "modules": modules
                })

    return dspy_modules

def extract_comments(module):
    '''
    Function to extract comments from modules.
    
    Args:
        module (str): The module from which comments are to be extracted.
        
    Returns:
        list: A list of comments extracted from the module.
    '''
    # Regex to match both inline comments (#) and docstrings (""" or ''')
    matches = re.findall(
        r"#.*?$|\"\"\"(.*?)\"\"\"|\'\'\'(.*?)\'\'\'",  # Match # comments and docstrings
        module,
        re.DOTALL | re.MULTILINE
    )
    # Separate out inline comments
    inline_comments = re.findall(r"#.*?$", module, re.MULTILINE)
    
    # Preserve the structure of docstrings as tuples
    docstrings = [match for group in matches for match in group if match]
    
    # Combine structured docstrings and inline comments
    all_comments = docstrings + inline_comments
    
    return all_comments

def make_df_with_metadata(data):
    '''
    Function to create a DataFrame with metadata from the data.
    
    Args:
        data (list): A list of dictionaries containing metadata about code files.
        
    Returns:
        DataFrame: A pandas DataFrame containing the metadata
    '''
    rows = []
    for entry in data:
        for module in entry["modules"]:
            rows.append({
                "repository": entry["repository"],
                "file_name": entry["file_name"],
                "file_path": entry["file_path"],
                "html_url": entry["html_url"],
                "module": module
            })
        df = pd.DataFrame(rows)
        df['module_context_length'] = df['module'].apply(len)
        df['comments'] = df['module'].apply(extract_comments)
    return df


def main():
    secrets = load_config(".secrets")
    GITHUB_API_TOKEN = secrets["auth"]["GITHUB_API_TOKEN"]
    HEADERS = {
                "Authorization": f"token {GITHUB_API_TOKEN}",
                "User-Agent": "DSPY Archiver"
            }
    query = "dspy.Module language:python"
    files = convert_to_json(HEADERS, query)  
    modules = extract_dspy_modules(files, HEADERS)

    df = make_df_with_metadata(modules)
    df.to_csv('script_archive/dspy_modules.csv', index=False)

if __name__ == "__main__":
    main()