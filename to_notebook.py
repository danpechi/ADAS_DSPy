import nbformat as nbf
import os

# def to_notebook_fn(nb, code_string):
#     """
#     Saves a Python code snippet as a Jupyter Notebook.

#     Args:
#         code_string (str): The Python code snippet to save in the notebook.
#         notebook_path (str): The name of the notebook file to save. Default is 'generated_notebook.ipynb'.
#         save_dir (str): Directory where the notebook will be saved. Default is the current directory.

#     Returns:
#         str: Full path to the saved notebook file.
#     """
#     nb['cells'].append(nbf.v4.new_code_cell(code_string))

dspy_model = 'agent'

install_commands = "%pip install dspy pyyaml\n%pip install --upgrade --force-reinstall databricks-vectorsearch \ndbutils.library.restartPython()"
imports = """
import json
import requests
from pyspark.sql import Row
import yaml

from databricks.vector_search.client import VectorSearchClient

import dspy
from dspy import Databricks
from dspy.retrieve.databricks_rm import DatabricksRM
import os
import pandas as pd

import mlflow
from mlflow import MlflowClient
"""
load_config = """
# Load the configuration
def load_config(config_path):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)  # Use safe_load to avoid arbitrary code execution
    return config

# Access the configuration
config = load_config("config.yaml")
secrets = load_config(".secrets")

# Access the configuration values
user_path = config["user"]["path"]
catalog_name = config["database"]["catalog_name"]
schema_name = config["database"]["schema_name"]
source_table_name = config["database"]["source_table_name"]

vector_search_endpoint_name = config["vector_search"]["endpoint_name"]
vs_index = config["vector_search"]["index"]

embedding_model_endpoint = config["models"]["embedding_model_endpoint"]
llm = config["models"]["llm"]

API_TOKEN = secrets["auth"]["api_token"]

registered_model_name = config["registered"]["model_name"]
registered_endpoint_name = config["registered"]["endpoint_name"]

API_ROOT = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
"""
endpoint_config_setup = """
# Set the name of the MLflow endpoint
endpoint_name = registered_endpoint_name

# Name of the registered MLflow model
model_name = registered_model_name

# Get the latest version of the MLflow model
mlflow_client = MlflowClient()
model_version = mlflow_client.search_model_versions(filter_string=f"name='{registered_model_name}'")[0].version

# Specify the type of compute (CPU, GPU_SMALL, GPU_LARGE, etc.)
workload_type = "CPU_SMALL"

# Specify the scale-out size of compute (Small, Medium, Large, etc.)
workload_size = "Small"

# Specify Scale to Zero(only supported for CPU endpoints)
scale_to_zero = False

# Get the API endpoint and token for the current notebook context
serving_host = spark.conf.get("spark.databricks.workspaceUrl")
"""
deploy_to_endpoint = """
# Deploy the model to a model serving endpoint in Databricks
data = {
    "name": endpoint_name,
    "served_entities": [
        {
            "entity_name": registered_model_name,
            "entity_version": model_version,
            "workload_size": workload_size,
            "scale_to_zero_enabled": scale_to_zero,
            "workload_type": workload_type,
            "environment_vars": {
                "DATABRICKS_TOKEN": f"{API_TOKEN}",
                "DATABRICKS_HOST": f"{API_ROOT}"
            }
        }
    ]
}

headers = {"Context-Type": "text/json", "Authorization": f"Bearer {API_TOKEN}"}

url = f"https://{serving_host}/api/2.0/serving-endpoints/{endpoint_name}/config"

response = requests.put(
    url=url, json=data, headers=headers
)

print(json.dumps(response.json(), indent=4))
"""

def make_notebook(user_message, class_def, class_name):
    save_dir = "."
    notebook_name = f"{class_name}_notebook.ipynb"
    os.makedirs(save_dir, exist_ok=True)
    full_path = os.path.join(save_dir, notebook_name)
    
    nb = nbf.v4.new_notebook()

    nb['cells'].append(nbf.v4.new_code_cell(install_commands))
    nb['cells'].append(nbf.v4.new_code_cell(imports))
    nb['cells'].append(nbf.v4.new_code_cell(load_config))
    nb['cells'].append(nbf.v4.new_code_cell(class_def))

    class_call = class_name + '()'
    agent_creation_string = f"""agent = {class_call}"""
    nb['cells'].append(nbf.v4.new_code_cell(agent_creation_string))

    ml_flow_input = user_message
    ml_flow_string = f"with mlflow.start_run():\n    # Log the model\n    model_info = mlflow.dspy.log_model(\n        dspy_model={dspy_model},\n        registered_model_name=registered_model_name,\n        artifact_path=\"model\",\n        input_example=\"{ml_flow_input}\",\n        pip_requirements=[\"dspy\"]\n    )"
    nb['cells'].append(nbf.v4.new_code_cell(ml_flow_string))
    nb['cells'].append(nbf.v4.new_code_cell(endpoint_config_setup))
    nb['cells'].append(nbf.v4.new_code_cell(deploy_to_endpoint))
    

    with open(full_path, 'w') as f:
        nbf.write(nb, f)

    return full_path
