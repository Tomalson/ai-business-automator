import os
from supabase import create_client, Client
from schemas import Lead

class DatabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def insert_lead(self, lead: Lead) -> dict:
        try:
            # Assuming 'leads' table in Supabase with columns matching Lead fields
            data = lead.dict()
            response = self.supabase.table('leads').insert(data).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            raise ValueError(f"Błąd podczas zapisywania do bazy: {str(e)}")