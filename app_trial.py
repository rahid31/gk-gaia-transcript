import streamlit as st
import pandas as pd
from fetch_api import fetch_and_flatten_chat_data

# Avatar/Icon paths
user_url = "data/image/user-square-1024.webp"
avatar_url = "data/image/nexa_icon_256.png"
page_icon = "data/image/lx_icon_192.png"

# Streamlit Page Configuration
st.set_page_config(
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon=page_icon,
    page_title="Learnext - NEXA Transcript"
)

# Hide Streamlit UI elements
st.markdown("""
    <style>
    header { visibility: hidden; }
    footer { visibility: hidden; }
    .st-emotion-cache-z5fcl4 { display: none; }
    .viewerBadge_container__1QSob {display: none !important;}
    .stDeployButton {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# Get session_id from URL
query_params = st.query_params
session_id = query_params.get("session_id", [""])[0] if isinstance(query_params.get("session_id"), list) else query_params.get("session_id")

# Load all chat data once
@st.cache_data
def load_chat_data():
    return fetch_and_flatten_chat_data()

df_all = load_chat_data()

# Main content
if session_id:
    # Filter by session
    df_session = df_all[df_all["chat_session_id"] == session_id]

    if not df_session.empty:
        created_at = df_session["start_chat"].min()
        user_email = df_session["user_email"].iloc[0]
        chat_topic = df_session.get("summary_title", "Topic not found").iloc[0] if "summary_title" in df_session else "Topic not found"
        summary = df_session.get("summary_content", "Summary not found").iloc[0] if "summary_content" in df_session else "Summary not found"

        st.subheader(chat_topic or "NEXA Transcript")

        with st.container():
            cols = st.columns([1, 1])
            with cols[0]:
                @st.cache_data
                def convert_df(df):
                    return df.to_csv(index=False).encode("utf-8")
                csv = convert_df(df_session)
                st.download_button("Download CSV", data=csv, file_name=f"nexa_transcript_{session_id}.csv", mime="text/csv")

        tabs = st.tabs(["Transcript", "Summary", "Session Details"])

        with tabs[0]:
            for _, row in df_session.iterrows():
                if pd.notna(row.get("msg_user")):
                    with st.chat_message("user", avatar=user_url):
                        st.write(row["msg_user"])
                if pd.notna(row.get("msg_avatar")):
                    with st.chat_message("assistant", avatar=avatar_url):
                        st.write(row["msg_avatar"])

        with tabs[1]:
            st.write(summary)

        with tabs[2]:
            st.write(f"**Session ID:** {session_id}")
            st.write(f"**User:** test@learnext.ai")
            st.write(f"**Created At:** {created_at}")

        st.divider()
        st.image("https://raw.githubusercontent.com/rahid31/gk-gaia-transcript/master/data/image/lx_primary_256.png", width=120)
    else:
        st.warning("No chat history found for this session ID.")
else:
    st.error("No session_id provided in the URL.")