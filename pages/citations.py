import streamlit as st
import app

app.initialize_streamlit_session()
app.local_css("style.css")
st.logo(image="kognitiv_spark_logo.png", icon_image="kognitiv_spark_logo.png")
st.title("Website References")


st.divider()

for citation in st.session_state.citations:
    with st.expander(f"Prompt: {citation['prompt']}"):
        for c in citation['citations']:
            st.markdown(f"""
                <div class="citation-container">
                    <p class="citation-title">Help Desk Reference {c['number']}:</p>
                    <a class="citation-link" href="{c['url']}" target="_blank">{c['url']}</a>
                </div>
            """, unsafe_allow_html=True)

