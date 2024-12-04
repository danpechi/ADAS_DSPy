# ADAS_DSPy

Abhinav Krishnan, Dan Pechi

A brief description of your project, its purpose, and its goals.

## Table of Contents

- [Usage](#usage)

## Usage

To generate the data, run the following three scripts in sequence:

1. **Github Search**: This script searches GitHub for code containing dspy.Module definitions.
   ```bash
   python github_search.py

2. **Extract dspy modules**: This script extracts the dspy.Module definitions from the search results.
   ```bash
   python make_dataset.py

3. **Github Serach**: This script saves the extracted dspy.Module definitions to a CSV file, along with some metadata. 
   ```bash
   python make_df.py
