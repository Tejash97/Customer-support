import requests
import streamlit as st
from dotenv import load_dotenv
import os
import json
from datetime import datetime


# Configuration (hidden from users)

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "64c49142-2edf-441a-b572-2ac085677c2e"
FLOW_ID = "22421405-024a-4c64-9700-c89341044c6f"
APPLICATION_TOKEN = "AstraCS:ZTRotIXRwCXeSulhwmztqYpI:951e69b422fa8f9aec9c1a0d0ec8d94b13cf00abd57f1780542ec5bb094e56a6"
ENDPOINT = "customersupport"

def run_flow(message: str) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}"
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "flow_id": FLOW_ID,
        "session_id": FLOW_ID,
        "use_custom_flow": True
    }
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json",
        "X-Flow-ID": FLOW_ID
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception("Unable to connect to support service. Please try again later.")

def extract_response(response_data: dict) -> str:
    try:
        return response_data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except (KeyError, IndexError) as e:
        raise Exception("Unexpected response format. Please try again.")

def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm your customer support assistant. How can I help you today?"
        })

def main():
    st.set_page_config(page_title="Customer Support", page_icon="💬", layout="centered")
    
    # Custom CSS for better UI and visibility
    st.markdown("""
        <style>
        /* Input field styling */
        .stTextInput>div>div>input {
            background-color: white;
            color: #333333;
            border: 1px solid #ddd;
        }
        
        /* Chat message containers */
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
            color: #333333;
        }
        
        /* Assistant message styling */
        .assistant {
            background-color: #E8F0FE;
            border: 1px solid #D2E3FC;
        }
        
        /* User message styling */
        .human {
            background-color: #F8F9FA;
            border: 1px solid #E9ECEF;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
        }
        
        .stButton>button:hover {
            background-color: #45a049;
        }
        
        /* Message sender name styling */
        .sender-name {
            font-weight: bold;
            color: #2C3E50;
            margin-bottom: 0.5rem;
        }
        
        /* Message content styling */
        .message-content {
            color: #333333;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("Customer Support ")
    st.markdown("---")

    # Initialize chat history
    initialize_chat_history()

    # Display chat messages
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "assistant":
                st.markdown(f"""
                    <div class="chat-message assistant">
                        <div class="sender-name">Support Agent</div>
                        <div class="message-content">{message["content"]}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message human">
                        <div class="sender-name">You</div>
                        <div class="message-content">{message["content"]}</div>
                    </div>
                """, unsafe_allow_html=True)

    # Chat input
    with st.container():
        col1, col2 = st.columns([4,1])
        
        with col1:
            user_input = st.text_input(
                "Type your message...",
                key="user_input",
                label_visibility="collapsed"
            )
        
        with col2:
            send_button = st.button("Send", use_container_width=True)

    # Handle send button
    if send_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        try:
            with st.spinner(""):
                response_data = run_flow(user_input)
                bot_response = extract_response(response_data)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": bot_response
                })
            
            st.rerun()
            
        except Exception as e:
            st.error("Sorry, I'm having trouble connecting. Please try again in a moment.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666666;'>
            Available 24/7 to assist you with your questions
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()