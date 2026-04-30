from pydantic import BaseModel
from typing import List, Optional, Dict

class ChatRequest(BaseModel):
    countryID: int
    questionText: str
    pillarID: Optional[int] = None