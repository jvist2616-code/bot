import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def save_generation(user_id, content_type, content, approved=False):
    data = {
        "user_id": user_id,
        "content_type": content_type,
        "content": content,
        "approved": approved
    }
    supabase.table("generations").insert(data).execute()
