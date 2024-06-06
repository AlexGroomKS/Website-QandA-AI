import direct_line as dl
import streamlit as st
import app
import time
# Display instructions for using the chat bot

def bot_response_animation(bot_response):
    placeholder = st.empty()
    animated_text = ""
    for char in bot_response:
        animated_text += char
        placeholder.markdown(animated_text)
        time.sleep(0.01)  

app.initialize_streamlit_session()

app.local_css("style.css")
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


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Type your message...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.reply_id = st.session_state.client.send_message(prompt)
    bot_response, citations = st.session_state.client.get_bot_response(st.session_state.reply_id)

    # Append bot's response and citations
    if bot_response:
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.session_state.citations.append({"prompt": prompt, "citations": citations})
        st.session_state.client.add_context(prompt)
        with st.chat_message("assistant"):
            bot_response_animation(bot_response)
        
    else:
        st.error("No response from bot.")
    st.rerun()  
