from datetime import datetime
from pydantic import BaseModel


class ApprovalResponse(BaseModel):
    id: int
    user_id: int
    request_type: str
    payload_json: str
    status: str
    reviewed_by: int | None
    reviewed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
