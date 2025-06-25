import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_and_flatten_chat_data():
    # Step 1: Fetch data from API
    URL = os.getenv("URL")
    HEADERS = {
        "X-Course-Secret-Key": os.getenv("SECRET_KEY")
    }

    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data. Status code: {response.status_code}, Error: {response.text}")

    data = response.json()
    df = pd.DataFrame(data)

    # Step 2: Parse chat_message JSON safely
    def ensure_parsed(x):
        if isinstance(x, str):
            try:
                return json.loads(x)
            except json.JSONDecodeError:
                return None
        return x

    df['chat_message'] = df['chat_message'].apply(ensure_parsed)

    # Step 3: Explode chat_message list into rows
    df_exploded = df.explode('chat_message', ignore_index=True)

    # Step 4: Flatten nested fields
    chat_df = pd.json_normalize(df_exploded['chat_message']).add_prefix('msg_')
    tenant_df = pd.json_normalize(df_exploded['tenant']).add_prefix('tenant_')
    user_df = pd.json_normalize(df_exploded['user']).add_prefix('user_')

    # Step 5: Drop original nested columns
    df_flat = df_exploded.drop(columns=['chat_message', 'tenant', 'user'])

    # Step 6: Combine everything
    df_final = pd.concat([df_flat, tenant_df, user_df, chat_df], axis=1)

    # Step 7: Select relevant columns
    keep_columns = [
        'chat_session_id', 'user_id', 'start_chat', 'end_chat',
        'tenant_slug', 'user_id', 'user_email',
        'msg_user', 'msg_avatar'
    ]
    df_final = df_final[keep_columns]

    return df_final
