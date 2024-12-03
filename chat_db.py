from openai import OpenAI
import streamlit as st
import requests
import json

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
            # print(response)
            # print(type(response))
            # Extract the prediction from the response
            # if "new_module" in response:
            assistant_message = response.new_module
            # else:
            #     assistant_message = "Unexpected response format."

            # Append the assistant's message to the session state
            st.write(assistant_message)
            # st.session_state.messages.append({"role": "assistant", "content": assistant_message})

        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
