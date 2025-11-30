from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    sender_id: str
    receiver_id: str
    content: str
    source_lang: str = "eng_Latn"
    target_lang: str = "spa_Latn"
    timestamp: Optional[float] = None

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str
