import nbformat as nbf
import os

def to_notebook_fn(code_string, notebook_name="generated_notebook.ipynb", save_dir="."):
    """
    Saves a Python code snippet as a Jupyter Notebook.

    Args:
        code_string (str): The Python code snippet to save in the notebook.
        notebook_path (str): The name of the notebook file to save. Default is 'generated_notebook.ipynb'.
        save_dir (str): Directory where the notebook will be saved. Default is the current directory.

    Returns:
        str: Full path to the saved notebook file.
    """
    os.makedirs(save_dir, exist_ok=True)
    full_path = os.path.join(save_dir, notebook_name)
    nb = nbf.v4.new_notebook()

    nb['cells'].append(nbf.v4.new_code_cell(code_string))

    with open(full_path, 'w') as f:
        nbf.write(nb, f)

    return full_path
