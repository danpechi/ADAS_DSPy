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
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an AI assistant"},
                    *st.session_state.messages
                ],
                model=st.session_state["openai_model"],
                max_tokens=256
            )
            assistant_message = chat_completion.choices[0].message.content
            st.write(assistant_message)
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
