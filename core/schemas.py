from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class Intent(str, Enum):
    browse_brands = "browse_brands"
    brand_details = "brand_details"
    order_status = "order_status"
    book_visit = "book_visit"
    clinical_advice = "clinical_advice"
    emergency = "emergency"
    off_topic = "off_topic"


class IntentResult(BaseModel):
    intent: Intent
    confidence: float = Field(default=0.5, ge=0, le=1)
    brand: Optional[str] = None
    category: Optional[str] = None
    order_id: Optional[str] = None
    reason: str = ""
    source: str = "rules"


class AgentReply(BaseModel):
    intent: Intent
    text: str
    blocked: bool = False
    tools_called: list[dict[str, Any]] = []
    trace: dict[str, Any] = {}
