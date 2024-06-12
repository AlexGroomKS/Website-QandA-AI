import streamlit as st
import requests
import time
from functools import wraps

replacement_dict = {
    "palm panel": ["panel", "palm panel", "palm"],
    "RemoteSpark": ["remote spark", "remotespark", "remote-spark", "Remote-Spark"],
    "Windows Device Portal": ["device portal", "windows portal", "windows device"],
    "User Guides": ["guides", "user manual", "instructions", "manual"],
    "Installing RemoteSpark via Sideload": ["install sideload", "sideload", "install RemoteSpark"],
    "Remote Assist": ["assist", "remote assist", "remote assistance"],
    #"Installation Guide": ["installation", "install guide", "install instructions"],
    "Troubleshooting Guide": ["troubleshoot", "troubleshooting", "problem solving", "error guide"],
    "Performance Optimization": ["optimization", "performance tuning", "performance", "optimize"],
    "RemoteSpark Voice Command": ["voice command", "speech command"],
    "Network Firewall Rules": ["firewall settings", "firewall configuration", "firewall rules", "firewall config", "firewall setup", "network rules", "network firewall"],
    "Windows Device Portal": ["device portal", "windows portal", "portal"]
}

# Function to replace terms in the query
def replace_terms_in_query(query, replacement_dict):
    try:
        for replacement, terms in replacement_dict.items():
            for term in terms:
                if term in query.lower():
                    query = query.lower().replace(term, replacement)
                    break  # Replace only the first matching term
        return query
    except Exception as e:
        print(f"Error in replace_terms_in_query: {e}")
        return query

# Decorator to rate limit the function
def rate_limited(max_per_second):
    """
    Decorator that rate-limits the function to be called up to max_per_second times per second.
    """
    min_interval = 1.0 / float(max_per_second)

    def decorate(func):
        last_time_called = [0.0]

        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            try:
                elapsed = time.clock() - last_time_called[0]
                left_to_wait = min_interval - elapsed

                if left_to_wait > 0:
                    time.sleep(left_to_wait)

                ret = func(*args, **kwargs)

                last_time_called[0] = time.clock()
                return ret
            except Exception as e:
                print(f"Error in rate_limited_function: {e}")
                return None

        return rate_limited_function

    return decorate

# --- Class to make direct line connection to the Copilot using Bot Framework functions ---
class DirectLineClient:
    def __init__(self, token):
        self.token = token
        self.conversation_id = None
        self.watermark = None
        self.context = []
        #self.citations = []

    def add_context(self, val):
        try:
            if val not in self.context:
                self.context.append(val)
            if len(self.context) > 10:  # Limit to last 10 context entries
                self.context.pop(0)
        except Exception as e:
            print(f"Error in add_context: {e}")

    def clear_context(self):
        try:
            self.context = []
        except Exception as e:
            print(f"Error in clear_context: {e}")

    def start_conversation(self):
        try:
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
                #self.watermark = conversation["watermark"]
        except Exception as e:
            print(f"Error in start_conversation: {e}")

    # Send a message to the bot, limited to 10 requests per second
    #@rate_limited(10)
    def send_message(self, message):
        try:
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
        except Exception as e:
            print(f"Error in send_message: {e}")
            return None

    # Get the bot's response, limited to 10 requests per second
    #@rate_limited(10)
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
            
            print(f'Activity: {activities[len(activities)-1]}')
            for activity in reversed(activities):
                if "name" in activity["from"] and "type" in activity and activity["type"] == "message":
                    if activity["replyToId"] == reply_to_id:
                        #if "OpenAIAdditionalInstructionsLengthExceededLimit" in activity["text"]:
                            #return "An error has occured, please try again later.", [], []
                        # Extract citations if they exist
                        citations = []
                        counter = 1
                        for entity in activity.get("entities", []):
                            if entity.get("type") == "https://schema.org/Message" and "citation" in entity:
                                for c in entity["citation"]:
                                    citations.append({"number": counter, "url": c["appearance"]["url"]})
                                    counter += 1

                        # Extract suggested actions if they exist
                        suggested_actions = []
                        if 'suggestedActions' in activity:
                            suggested_actions = activity['suggestedActions'].get('actions', [])

                        return activity["text"], citations, suggested_actions
            time.sleep(interval)

        return None, [], []
        

# Function to get a token for the Copilot
def get_copilot_token(token_endpoint):
    response = requests.get(token_endpoint)
    response.raise_for_status()
    return response.json()['token']


