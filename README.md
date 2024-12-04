# ADAS_DSPy

**Abhinav Krishnan**, **Dan Pechi**

We create an LLM-agent creator powered by another agent, that can generate code for you based on your requirements. The agent-creator is powered by a large language model (LLM) that is performing retrieval on a dataset of dspy.Module definitions. The agent-creator comes with a front-end chat interface that allows you to ask for code snippets, and will generate the code for you. The dataset was created by scraping GitHub for code containing dspy.Module definitions.

## Usage

### Installation
Clone the repository:
```bash
git clone https://github.com/danpechi/ADAS_DSPy.git
```

To install the required packages, run the following command:
```bash
pip install -r requirements.txt
```

### Environment Setup

1. **GitHub API**: 
   Create a file called `.secrets` in the root directory of the project. 
   Generate a GitHub API token, and then add the following line to the file:
   ```
   "GITHUB_API_TOKEN": "<YOUR_API_TOKEN>"
   ```
2. **DataBricks Token**:
   Create a folder called `.streamlit`, and create a file called `secrets.toml` inside it.
   Add the following lines to the file:
   ```
   DB_TOKEN = "<YOUR_DB_TOKEN>"
   ```
### Data Generation

To generate the data, run the following command:

   ```bash
   python make_archive.py
   ```
   This script searches GitHub for code containing dspy.Module definitions, extracts the dspy.Module definitions from the search results and saves the extracted dspy.Module definitions to a CSV file, along with some metadata. 

### Deploy Agent Creator

To deploy the agent creator LLM model, run the cells in the `setup_notebook.ipynb` notebook.

### Open Chat Interface

To open the chat interface, run the following command:
```bash
streamlit run chat-db.py
```
You can now ask the chat interface to give you the code for an agent that you want!



Inspired by https://arxiv.org/abs/2408.08435