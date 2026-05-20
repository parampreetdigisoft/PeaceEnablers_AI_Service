from typing import Optional
from pydantic import BaseModel

class MissingPillarQuestionRequest(BaseModel):
    country_id: int
    pillar_id: Optional[int] = None