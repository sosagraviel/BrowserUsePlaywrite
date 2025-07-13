from pydantic import BaseModel
from typing import Optional

class CheckoutResult(BaseModel):
    success: bool
    message: str
    list_of_questions: list[str]
    extracted_content: Optional[str] = None 