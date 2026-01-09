from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Lead(BaseModel):
    name: Optional[str] = Field(None, description="Imię i nazwisko")
    company: Optional[str] = Field(None, description="Nazwa firmy (jeśli klient biznesowy)")
    email: Optional[EmailStr] = Field(None, description="Email")
    phone: Optional[str] = Field(None, description="Telefon")
    product: Optional[str] = Field(None, description="Produkt (Fotowoltaika/Pompa/Inne)")
    budget_est: Optional[str] = Field(None, description="Budżet")
    urgency: Optional[str] = Field(None, description="Pilność")
    city: Optional[str] = Field(None, description="Miasto")
    summary: Optional[str] = Field(None, description="Podsumowanie")
    score: int = Field(..., ge=1, le=10, description="Ocena 1-10")
class LeadInput(BaseModel):
    text: str = Field(..., description="Nieustrukturyzowany tekst z maila lub wiadomości")