import streamlit as st
import json
import os
import pandas as pd

# Path to the JSON file
JSON_FILE_PATH_1 = r"data\avatar-log-chat-20250320.json"
JSON_FILE_PATH_2 = r"data\gaia-summary-content-20250320.json"

# Avatar Icon
user_url = r"data\image\user-square-1024.webp"
avatar_url = r"data\image\Logo GAIA.png"

# Function to fetch chat history from the JSON file
def fetch_chat_history(session_id):
    
    if not os.path.exists(JSON_FILE_PATH_1):
        st.error("Chat data file not found.")
        return []
    
    with open(JSON_FILE_PATH_1, "r", encoding="utf-8") as file:
        try:
            chat_data = json.load(file)
        except json.JSONDecodeError:
            st.error("Error reading JSON file.")
            return []
    
    # Extract chat history for the given session_id
    session_chats = [entry for entry in chat_data if entry.get("chat_session_id") == session_id]
    
    return session_chats

# Function to fetch summary content from the JSON file
def fetch_summary_content(session_id):
    
    if not os.path.exists(JSON_FILE_PATH_2):
        st.error("Summary data file not found.")
        return []
    
    with open(JSON_FILE_PATH_2, "r", encoding="utf-8") as file:
        try:
            summary_data = json.load(file)
        except json.JSONDecodeError:
            st.error("Error reading JSON file.")
            return []
    
    # Extract chat history for the given session_id
    summary_content = [entry for entry in summary_data if entry.get("chat_session_id") == session_id]
    
    return summary_content

### Page Configuration
st.set_page_config(
    layout="centered", # Pick either centered or wide as default 
    initial_sidebar_state="collapsed" # Sidebar close default
)

# Get session_id from URL parameters
query_params = st.query_params
session_id = query_params.get("session_id", [""])[0] if isinstance(query_params.get("session_id"), list) else query_params.get("session_id")

# Session Details
if session_id:
    chat_history = fetch_chat_history(session_id)
    summary_content = fetch_summary_content(session_id)
    
    if chat_history:
        if chat_history and isinstance(chat_history[0], dict):
            created_at = chat_history[0].get("created_at", "Unknown Date")
            chat_topic = chat_history[0].get("summary_title", "Topic not found.")
            user_email = chat_history[0].get("user_email", "Email not found.")
        else:
            created_at = "Unknown Date"
            chat_topic = "Topic not found."
            user_email = "Email not found."

        if summary_content and isinstance(summary_content[0], dict):
            summary = summary_content[0].get("summary_content", "Summary not found.")
        else:
            summary = "Summary not found."

### Page UI
        # Title
        if chat_topic is None:
            st.subheader(chat_topic)
        else:
            st.subheader("GAIA Transcript")

        # st.markdown("---")

        st.sidebar.title("Session Details")
        # st.subheader("Session Details:")

        st.sidebar.write("")

        st.sidebar.write(f" **Session ID:**\n\n{session_id}")
        st.sidebar.write(f" **User:**\n\n{user_email}")
        # st.sidebar.write(f" **Topic:** {chat_topic}")
        st.sidebar.write(f" **Created At:**\n\n{created_at}")
        st.sidebar.write("\n" * 5)

        # theme = st.sidebar.radio("Choose a theme:", ["Light", "Dark"])

        st.write("")

        with st.container():
            cols = st.columns([1,1])

            with cols[0]:               
                df = pd.DataFrame(chat_history)
                columns = ["chat_session_id", "user_email", "user", "avatar"]
                df = df[columns]
                
                @st.cache_data
                def convert_df(df):
                    return df.to_csv(index=False).encode('utf-8')
                
                # Download .csv button
                csv = convert_df(df)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"gaia_transcript_{session_id}.csv",
                    mime="text/csv",
                )
            
        st.write("")

        tabs = st.tabs(["Transcript", "Summary"])

        # Transcript
        with tabs[0]:
            # st.subheader("Transcripts:")
            st.write("")

            # Message Display    
            for chat in chat_history:
                if "user" in chat:
                    with st.chat_message("user", avatar=user_url):
                        st.write(chat["user"])
                    st.write("")
                if "avatar" in chat:
                    with st.chat_message("assistant", avatar=avatar_url):
                        st.write(chat["avatar"])

        with tabs[1]:
            st.write("")
            
            if summary:
                st.write(summary)
            else:
                st.warning("No summary found for this session.")

        # st.write("\n" * 3)

        # gK logo as footer
        st.divider()
        col1, col2 = st.columns([1,3])

        with col1:
            st.image("https://gk-analyst.s3.ap-southeast-1.amazonaws.com/metabase-dashboard/gokampus_logo.svg", width = 100)  # Adjust width
    else:
        st.warning("No chat history found for this session.")
else:
    st.error("No session_id provided in the URL.")