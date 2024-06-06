import streamlit as st

import requests
import time
# Token endpoint
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

# --- Class to make direct line connection to the Copilot using Bot Framework functions ---
class DirectLineClient:
    def __init__(self, token):
        self.token = token
        self.conversation_id = None
        self.watermark = None
        self.context = []
        #self.citations = []
    
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

    def get_bot_response(self, reply_to_id, polling_interval_type='client'):
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
            
            for activity in reversed(activities):
                if "name" in activity["from"]:
                    if activity["replyToId"] == reply_to_id:
                        # Extract citations if they exist
                        citations = []
                        counter = 1
                        for entity in activity.get("entities", []):
                            if entity.get("type") == "https://schema.org/Message" and "citation" in entity:
                                for c in entity["citation"]:
                                    citations.append({"number": counter, "url": c["appearance"]["url"]})
                                    counter += 1
                    
                        return activity["text"], citations
            time.sleep(interval)

        return None

# Function to get a token for the Copilot
def get_copilot_token(token_endpoint):
    response = requests.get(token_endpoint)
    response.raise_for_status()
    return response.json()['token']


