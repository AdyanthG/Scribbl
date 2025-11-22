import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class StorageManager:
    def __init__(self, bucket_name: str = "sketchcourse"):
        self.bucket = bucket_name

    def upload_file(self, file_path: str, dest_path: str) -> str:
        with open(file_path, "rb") as f:
            res = supabase.storage.from_(self.bucket).upload(dest_path, f)

        if "error" in str(res).lower():
            raise Exception(f"Upload failed: {res}")

        # Return public signed URL
        signed = supabase.storage.from_(self.bucket).create_signed_url(
            dest_path, expires_in=604800   # 7 days
        )
        return signed["signedURL"]

    def download_file(self, src_path: str, dest_path: str):
        data = supabase.storage.from_(self.bucket).download(src_path)
        with open(dest_path, "wb") as f:
            f.write(data)

    def delete_file(self, path: str):
        supabase.storage.from_(self.bucket).remove(path)

    def save_json(self, path: str, data: dict):
        import json
        json_str = json.dumps(data)
        # Upload as string
        res = supabase.storage.from_(self.bucket).upload(
            path, 
            json_str.encode(), 
            {"content-type": "application/json", "upsert": "true"}
        )
        if "error" in str(res).lower():
            raise Exception(f"Upload failed: {res}")

    def get_json(self, path: str) -> dict:
        import json
        try:
            data = supabase.storage.from_(self.bucket).download(path)
            return json.loads(data)
        except Exception as e:
            print(f"Error reading JSON {path}: {e}")
            return None
