# chat.py
import direct_line as dl
import streamlit as st
import app
import time
import streamlit.components.v1 as components

# Display instructions for using the chat bot
def bot_response_animation(bot_response):
    placeholder = st.empty()
    animated_text = ""
    for char in bot_response:
        animated_text += char
        placeholder.markdown(animated_text)
        time.sleep(0.01)  

def move_focus():
    components.html(
        """
        <script>
            var textarea = window.parent.document.querySelectorAll("textarea[type=textarea]");
            for (var i = 0; i < textarea.length; ++i) {
                textarea[i].focus();
            }
        </script>
        """,
    )

app.initialize_streamlit_session()
app.local_css("style.css")
st.logo(image="kognitiv_spark_logo.png", icon_image="kognitiv_spark_logo.png")
st.title("AI Q&A Chat Bot")

st.divider()

# Sidebar setup
if st.sidebar.button("Clear Conversation", key='clear_chat_button'):
    st.session_state.messages = []
    move_focus()
if st.sidebar.button("Show Example Conversation", key='show_example_conversation'):
    example_user_prompts = [
        "How do I use the windows device portal?",
        "What are the installation steps for sideloading RemoteSpark?",
    ]
    for i, up in enumerate(example_user_prompts):
        st.session_state.messages.append({"role": "user", "content": up})
        st.session_state.reply_id = st.session_state.client.send_message(up)
        bot_response, citations, suggested_actions = st.session_state.client.get_bot_response(st.session_state.reply_id)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
    move_focus()

# Placeholder for chat messages
chat_placeholder = st.empty()

def display_chat():
    with chat_placeholder.container():
        for idx, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Typing animation
def typing_animation(placeholder):
    animation_steps = ["", ".", "..", "..."]
    for step in animation_steps:
        placeholder.markdown(f"Fetching a response{step}")
        time.sleep(0.5)

# Function to handle suggested action click
def handle_suggested_action(action_value):
    st.session_state.messages.append({"role": "user", "content": action_value})
    with st.chat_message("user"):
        st.markdown(action_value)

    loading_placeholder = st.empty()
    with loading_placeholder.container():
        with st.chat_message("assistant"):
            typing_animation(loading_placeholder)

    st.session_state.reply_id = st.session_state.client.send_message(action_value)
    bot_response, citations, suggested_actions = st.session_state.client.get_bot_response(st.session_state.reply_id)

    loading_placeholder.empty()

    if bot_response:
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.session_state.citations.append({"prompt": action_value, "citations": citations})
        st.session_state.client.add_context(action_value)
        st.session_state["suggested_actions"] = suggested_actions
        with st.chat_message("assistant"):
            bot_response_animation(bot_response)
    else:
        st.error("No response from bot.")

# Initial display of chat messages
display_chat()

# Input for new user message
prompt = st.chat_input("Type your message...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    loading_placeholder = st.empty()
    with loading_placeholder.container():
        with st.chat_message("assistant"):
            typing_animation(loading_placeholder)

    st.session_state.reply_id = st.session_state.client.send_message(prompt)
    bot_response, citations, suggested_actions = st.session_state.client.get_bot_response(st.session_state.reply_id)

    loading_placeholder.empty()

    if bot_response:
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.session_state.citations.append({"prompt": prompt, "citations": citations})
        st.session_state.client.add_context(prompt)
        st.session_state["suggested_actions"] = suggested_actions
        with st.chat_message("assistant"):
            bot_response_animation(bot_response)
    else:
        st.error("No response from bot.")
    st.rerun()

# Display suggested actions as buttons below the chat input
if "suggested_actions" in st.session_state and st.session_state["suggested_actions"]:
    cols = st.columns(len(st.session_state["suggested_actions"]), gap="small")
    for idx, action in enumerate(st.session_state["suggested_actions"]):
        if cols[idx].button(action["title"], key=f"action_{idx}"):
            handle_suggested_action(action["value"])
