import json
import re
import pandas as pd


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
    with open('script_archive/dspy_modules.json', 'r') as f:
        data = json.load(f)
    df = make_df_with_metadata(data)
    df.to_csv('script_archive/dspy_modules.csv', index=False)
    
if __name__ == "__main__":
    main()
    