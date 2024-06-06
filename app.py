import direct_line as dl
import streamlit as st

def initialize_streamlit_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "client" not in st.session_state:
        token = dl.get_copilot_token(st.secrets["token_endpoint"])
        st.session_state.client = dl.DirectLineClient(token)
        st.session_state.client.start_conversation()

    if "reply_id" not in st.session_state:
        st.session_state.reply_id = ''
    
    if "citations" not in st.session_state:
        st.session_state.citations = []
    if "pending_response" not in st.session_state:
        st.session_state.pending_response = False

def display_instructions():
    st.markdown('''
        ### Here are some instructions to help you get started
        ''')
    st.markdown('''
        - Type your message in the input box below and press Enter to send it.
        - The bot will respond to your message and the conversation history will be displayed above.
        - Use specific keywords or phrases for better responses.
        - If you need to start a new conversation, enter "restart" then "yes".
    ''')

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

initialize_streamlit_session()

# Add company logo and title
st.logo(image="kognitiv_spark_logo.png", icon_image="kognitiv_spark_logo.png")

st.title("Kognitiv Spark Help Desk Q&A")

col1, col2, col3 = st.columns(3)
with col1:
    st.page_link("app.py", label="Home")
with col2:
    st.page_link("pages/chat.py", label="Chat")
with col3:
    st.page_link("pages/citations.py", label="References")
st.divider()
with st.container():
    display_instructions()
    
