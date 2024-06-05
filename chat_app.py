import streamlit as st

import requests
import time
# Token endpoint
TOKEN_ENDPOINT = "" #input Copilot token endpoint
replacement_dict = {
    "palm panel": ["panel", "palm panel", "palm"],
    "RemoteSpark": ["spark", "remote", "remote spark"],
    "Network Firewall Rules": ["firewall", "network rules", "firewall rules", "network firewall"],
    "Windows Device Portal": ["device portal", "windows portal", "windows device"],
    "User Guides": ["guides", "user manual", "instructions", "manual"],
    "Installing RemoteSpark via Sideload": ["install sideload", "sideload", "install RemoteSpark"],
    "Remote Assist": ["assist", "remote assist", "remote assistance"],
    #"Configuration Settings": ["settings", "configuration", "config"],
    #"User Authentication": ["login", "authentication", "user login"],
    "Installation Guide": ["installation", "install guide", "install instructions"],
    "Troubleshooting Guide": ["troubleshoot", "troubleshooting", "problem solving", "error guide"],
    "Performance Optimization": ["optimization", "performance tuning", "performance", "optimize"],
    "RemoteSpark Voice Command": ["voice command", "speech command"],
    "Network Firewall Rules": ["firewall settings", "firewall configuration", "firewall rules", "firewall config", "firewall setup"],
    "Windows Device Portal": ["device portal", "windows portal", "portal"]
}

def replace_terms_in_query(query, replacement_dict):
    for replacement, terms in replacement_dict.items():
        for term in terms:
            if term in query.lower():
                query = query.lower().replace(term, replacement)
                break  # Replace only the first matching term
    return query

class DirectLineClient:
    def __init__(self, token):
        self.token = token
        self.conversation_id = None
        self.watermark = None
        self.context = []
    
    def add_context(self, val):
        if val not in self.context:
            self.context.append(val)
        if len(self.context) > 10:  # Limit to last 10 context entries
            self.context.pop(0)

    def clear_context(self):
        self.context = []

    def start_conversation(self):
        self.clear_context()
        if not self.conversation_id:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            response = requests.post("https://directline.botframework.com/v3/directline/conversations", headers=headers)
            response.raise_for_status()
            conversation = response.json()
            self.conversation_id = conversation["conversationId"]

    def send_message(self, message):

        message = replace_terms_in_query(message, replacement_dict)

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        payload = {
            "locale": "en-US",
            "type": "message",
            "from": {
                "id": "user1"
            },
            "text": message,
            "entities": [{"type": "context", "value": self.context}] if self.context else []
        }
        url = f"https://directline.botframework.com/v3/directline/conversations/{self.conversation_id}/activities"
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['id']

    def get_bot_response_sync(self, reply_to_id, polling_interval_type='client'):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        url = f"https://directline.botframework.com/v3/directline/conversations/{self.conversation_id}/activities"

        # Poll for the bot's response
        polling_intervals = {
            'service': 5,  # seconds
            'client': 1   # seconds
        }

        interval = polling_intervals.get(polling_interval_type, 1)
        max_attempts = 10

        for _ in range(max_attempts):
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            activities = response.json().get("activities", [])
            print(f'Activities:\n{activities}')
            for activity in reversed(activities):
                # Ensure we get responses from the bot and not echo messages
                if "name" in activity["from"]:
                    if activity["replyToId"] == reply_to_id:
                        return activity["text"]
            time.sleep(interval)

        return None

# Function to get a token for your Copilot
def get_copilot_token(token_endpoint):
    response = requests.get(token_endpoint)
    response.raise_for_status()
    return response.json()['token']

# Streamlit app
st.title("Bot Chat App")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize DirectLineClient
if "client" not in st.session_state:
    token = get_copilot_token(TOKEN_ENDPOINT)
    st.session_state.client = DirectLineClient(token)
    st.session_state.client.start_conversation()

if "reply_id" not in st.session_state:
    st.session_state.reply_id = ''


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input("Type your message...")

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    context = st.session_state.messages

    # Send user message to bot and get response
    st.session_state.reply_id = st.session_state.client.send_message(prompt)
    bot_response = st.session_state.client.get_bot_response_sync(st.session_state.reply_id)
    
    st.session_state.client.add_context(prompt)

    if bot_response:
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(bot_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    else:
        # Handle the case where no response is received
        st.error("No response from bot.")


#if st.button("Start New Conversation", help="Start a new conversation"):
 #   st.session_state.client.start_conversation()
  #  st.session_state.messages = []
   # st.session_state.reply_id = ''
    #st.experimental_rerun()
