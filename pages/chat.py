# chat.py
# Importing necessary libraries
import direct_line as dl
import streamlit as st
import app
import time
import streamlit.components.v1 as components

# Function to animate bot responses
def bot_response_animation(bot_response):
    # Create an empty placeholder
    placeholder = st.empty()
    
    animated_text = ""
    # Loop through each character in the bot response
    for char in bot_response:
        # Add the character to the animated text
        animated_text += char
        # Display the animated text in the placeholder
        placeholder.markdown(animated_text)
        # Pause for a short time to create the animation effect
        time.sleep(0.01)

# Function to move focus to the textarea
def move_focus():
    # Use HTML and JavaScript to select all textareas and focus on them
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

# Initialize the Streamlit session, Apply the CSS styles from style.css, Display the logo, and Set the title of the Streamlit app
app.initialize_streamlit_session()
app.local_css("style.css")
st.logo(image="kognitiv_spark_logo.png", icon_image="kognitiv_spark_logo.png")
st.title("AI Q&A Chat Bot")

# Add a divider for visual separation
st.divider()

# Setup the sidebar, add buttons to clear the conversation and show an example conversation
if st.sidebar.button("Start New Conversation", key='clear_chat_button'):
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
#def typing_animation(placeholder):
 #   animation_steps = ["", ".", "..", "..."]
  #  for step in animation_steps:
   #     placeholder.markdown(f"Fetching a response{step}")
    #    time.sleep(0.5)

# Function to handle suggested action click
def handle_suggested_action(action_value):
    st.session_state["suggested_actions"] = [] 
    st.session_state.messages.append({"role": "user", "content": action_value})
    with st.chat_message("user"):
        st.markdown(action_value)

    #loading_placeholder = st.empty()
    #with loading_placeholder.container():
     #   with st.chat_message("assistant"):
      #      typing_animation(loading_placeholder)
    try:
        st.session_state.reply_id = st.session_state.client.send_message(action_value)
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return
    
    try:
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            with st.chat_message("assistant"):
                with st.spinner("Fetching response..."):
                    bot_response, citations, suggested_actions = st.session_state.client.get_bot_response(st.session_state.reply_id)
    except Exception as e:
        st.error(f"Error getting bot response: {e}")
        return
    
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

    st.session_state.reply_id = st.session_state.client.send_message(prompt)

    loading_placeholder = st.empty()
    with loading_placeholder.container():
        with st.chat_message("assistant"):
            with st.spinner("Fetching response..."):
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
