import re
from openai import OpenAI
import streamlit as st
from to_notebook import make_notebook

st.title("ChatGPT-like clone")

# Initialize OpenAI client with Databricks endpoint
client = OpenAI(
    api_key=st.secrets["DB_TOKEN"],
    base_url="https://eng-ml-inference-batch-inference-us-west-2.cloud.databricks.com/serving-endpoints"
)

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "ADAS_endpoint"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Combine the chat history into a single input string
            user_message = st.session_state.messages[-1]["content"] if st.session_state.messages else ""

            # Send request to the Databricks model endpoint
            response = client.chat.completions.create(
                messages=[
                    {"inputs": [user_message]},
                ],
                model=st.session_state["openai_model"],
                max_tokens=256
            )

            # Extract the prediction from the response
            assistant_message = response.new_module

            # Append the assistant's message to the session state
            st.write(assistant_message)

            # Create the notebook with the code
            class_def_pattern = r'class\s+\w+\s?\(.*\)\s*:\s*(.*?)(?=\n\s*class\s|\Z)'
            class_def_match = re.search(
                class_def_pattern, assistant_message, re.DOTALL)
            class_def = class_def_match.group(0).strip()
            class_def = re.sub(r'`', '', class_def)
            # Search for the first class definition
            match = re.search(class_def_pattern, assistant_message, re.DOTALL)

            class_name_pattern = r'class\s+(\w+)\s*(?:\(|:)'
            class_name_match = re.search(class_name_pattern, assistant_message)
            class_name = class_name_match.group(1)
            make_notebook(user_message, class_def, class_name)

        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_message})
