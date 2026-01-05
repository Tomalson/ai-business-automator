import os
import logging
from supabase import create_client, Client
from schemas import Lead

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def insert_lead(self, lead: Lead) -> dict:
        try:
            logger.info("Inserting lead into database")
            # Assuming 'leads' table in Supabase with columns matching Lead fields
            data = lead.dict()
            response = self.supabase.table('leads').insert(data).execute()
            logger.info("Lead inserted successfully")
            return {"success": True, "data": response.data}
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            raise ValueError(f"Błąd podczas zapisywania do bazy: {str(e)}")