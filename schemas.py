from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Lead(BaseModel):
    name: Optional[str] = Field(None, description="Imię i nazwisko potencjalnego klienta")
    email: Optional[EmailStr] = Field(None, description="Adres email")
    phone: Optional[str] = Field(None, description="Numer telefonu")
    product: Optional[str] = Field(None, description="Produkt lub usługa, którą klient jest zainteresowany")
    budget_est: Optional[str] = Field(None, description="Szacunkowy budżet (np. '5000-10000 PLN')")
    urgency: Optional[str] = Field(None, description="Pilność (np. 'Wysoka', 'Średnia', 'Niska')")
    city: Optional[str] = Field(None, description="Miasto")
    summary: Optional[str] = Field(None, description="Podsumowanie zapytania")
    score: int = Field(..., ge=1, le=10, description="Ocena priorytetu leada od 1 do 10")

class LeadInput(BaseModel):
    text: str = Field(..., description="Nieustrukturyzowany tekst z maila lub wiadomości")