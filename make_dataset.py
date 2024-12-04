import re
import os
import requests
import json
import base64
from dotenv import load_dotenv
import time
from tqdm import tqdm

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

def extract_dspy_modules(input_file, output_file, headers):
    """
    Extracts dspy.Module classes from files listed in a JSON file and saves the results to another JSON file.

    Args:
        input_file (str): Path to the input JSON file containing file metadata.
        output_file (str): Path to save the output JSON file with extracted modules.

    
    Returns:
        str: The path to the saved output JSON file.
    """
    # Load the existing dspy_code_snippets data
    with open(input_file, "r") as f:
        dspy_code_snippets = json.load(f)

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

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(dspy_modules, f, indent=4)

    print(f"Results saved to {output_file}")
    return output_file

def main():
    load_dotenv()
    TOKEN = os.getenv('GITHUB_TOKEN')
    HEADERS = {
                "Authorization": f"token {TOKEN}",
                "User-Agent": "DSPY Archiver"
            }
    search_output_file = "script_archive/dspy_code_snippets.json"
    dspy_module_output_file = "script_archive/dspy_modules.json"
    
    extract_dspy_modules(search_output_file, dspy_module_output_file, HEADERS)


if __name__ == "__main__":
    main()