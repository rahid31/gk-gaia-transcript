import streamlit as st
import json
import requests
import pandas as pd

# Use RAW GitHub URLs for JSON files
JSON_FILE_PATH_1 = "https://raw.githubusercontent.com/rahid31/gk-gaia-transcript/master/data/avatar-log-chat.json"
JSON_FILE_PATH_2 = "https://raw.githubusercontent.com/rahid31/gk-gaia-transcript/master/data/gaia_summary_content.json"

# Avatar Icon
user_url = "data/image/user-square-1024.webp"
avatar_url = "data/image/Logo GAIA.png"
page_icon = "data/image/lx_icon_192.png"

# Function to fetch JSON from GitHub
def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch data: {e}")
        return []

# Fetch chat history
def fetch_chat_history(session_id):
    chat_data = fetch_json(JSON_FILE_PATH_1)
    return [entry for entry in chat_data if entry.get("chat_session_id") == session_id]

# Fetch summary content
def fetch_summary_content(session_id):
    summary_data = fetch_json(JSON_FILE_PATH_2)
    return [entry for entry in summary_data if entry.get("chat_session_id") == session_id]

# Streamlit Page Configuration
st.set_page_config(layout="centered", initial_sidebar_state="collapsed", page_icon=page_icon, page_title="goKampus - GAIA Transcript")

# Get session_id from URL
query_params = st.query_params
session_id = query_params.get("session_id", [""])[0] if isinstance(query_params.get("session_id"), list) else query_params.get("session_id")

# Fetch Data
if session_id:
    chat_history = fetch_chat_history(session_id)
    summary_content = fetch_summary_content(session_id)

    # Handle missing data
    if chat_history:
        created_at = chat_history[0].get("created_at", "Unknown Date")
        user_email = chat_history[0].get("user_email", "Email not found.")
    else:
        created_at, user_email = "Unknown Date", "Email not found."

    summary = summary_content[0].get("summary_content", "Summary not found.") if summary_content else "Summary not found."
    chat_topic = summary_content[0].get("summary_title", "Topic not found.") if summary_content else "Topic not found."

    # Page UI

    #Hide Toolbar & footer
    st.markdown("""
        <style>
        header { visibility: hidden; }
        footer { visibility: hidden; }
        .st-emotion-cache-z5fcl4 { display: none; }  /* Hides Streamlit toolbar */
        .viewerBadge_container__1QSob {display: none !important;} /* Hides 'Created by' and 'Hosted by' */
        .stDeployButton {display: none !important;} /* Hides deploy/share button */
        </style>
    """, unsafe_allow_html=True)

    st.subheader(chat_topic if chat_topic else "GAIA Transcript")
    
    st.write("")
    with st.container():
        cols = st.columns([1, 1])

        with cols[0]:
            if chat_history:
                df = pd.DataFrame(chat_history)

                @st.cache_data
                def convert_df(df):
                    return df.to_csv(index=False).encode("utf-8")

                csv = convert_df(df)
                st.download_button("Download CSV", data=csv, file_name=f"gaia_transcript_{session_id}.csv", mime="text/csv")

    # Tabs
    tabs = st.tabs(["Transcript", "Summary", "Session Details"])
    with tabs[0]: # Transcript Tab
        for chat in chat_history:
            if "user" in chat:
                with st.chat_message("user", avatar=user_url):
                    st.write(chat["user"])
                    st.write("")
            if "avatar" in chat:
                with st.chat_message("assistant", avatar=avatar_url):
                    st.write(chat["avatar"])
                    st.write("")

    with tabs[1]: # Summary Tab
        st.write(summary)

    with tabs[2]: # Session Details Tab
        st.write(f"**Session ID:** {session_id}")
        st.write(f"**User:** {user_email}")
        st.write(f"**Created At:** {created_at}")

    # Footer
    st.divider()
    st.image(r"data\image\lx_primary_256.png", width=120)

else:
    st.error("No session_id provided in the URL.")