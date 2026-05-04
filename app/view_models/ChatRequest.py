from pydantic import BaseModel
from typing import List, Optional, Dict

class ChatRequest(BaseModel):
    countryID: int
    questionText: str
    historyText: Optional[str] = None
    pillarID: Optional[int] = None

class ChatGlobalRequest(BaseModel):
    questionText: str
    historyText: Optional[str] = None
    faqid: Optional[int] = None

class ChatCountryRequest(BaseModel):
    countryID: int
    questionText: str
    historyText: Optional[str] = None
    faqid: Optional[int] = None
    pillarID: Optional[int] = None