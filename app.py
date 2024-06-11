import direct_line as dl
import streamlit as st

def initialize_streamlit_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "client" not in st.session_state:
        token = dl.get_copilot_token("https://defaultfc30585e9c6d4255b46a16cfe906bb.56.environment.api.powerplatform.com/powervirtualagents/botsbyschema/cra44_remoteSparkWebsiteQACopilot/directline/token?api-version=2022-03-01-preview")
        st.session_state.client = dl.DirectLineClient(token)
        st.session_state.client.start_conversation()

    if "reply_id" not in st.session_state:
        st.session_state.reply_id = ''
    
    if "citations" not in st.session_state:
        st.session_state.citations = []
    if "suggested_actions" not in st.session_state:
        st.session_state.suggested_actions = []

    if "pending_response" not in st.session_state:
        st.session_state.pending_response = False
    if "clear_chat_disabled" not in st.session_state:
        st.session_state.clear_chat_disabled = False
    if "example_conversation_disabled" not in st.session_state:
        st.session_state.example_conversation_disabled = False

def display_instructions():
    st.markdown('''
        ### Overview
        ''')
    st.markdown('''
        - The bot will respond to your message and will provide references from https://help.kognitivspark.com/
        - Use specific keywords or phrases for better responses
        - Go to the references page to view the references provided by the bot for each prompt
        - If you need to start a new conversation click on the "Start New Conversation" button on the sidebar while on the chat page
    ''')

# Load custom CSS
def local_css(file_name):
    with open(file_name) as file_in:
        st.markdown(f'<style>{file_in.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

initialize_streamlit_session()

# Add company logo and title
st.logo(image="kognitiv_spark_logo.png", icon_image="kognitiv_spark_logo.png")

st.title("Kognitiv Spark Help Desk Q&A")


st.divider()
with st.container():
    display_instructions()
    
