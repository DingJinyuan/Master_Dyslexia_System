import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.core.security import hash_password
from app.db.session import get_db
from app.models.approval import ApprovalRequest
from app.models.user import User
from app.schemas.admin import ApprovalResponse
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/approval-requests", response_model=list[ApprovalResponse])
def list_approval_requests(db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    return db.query(ApprovalRequest).order_by(ApprovalRequest.created_at.desc()).all()


@router.post("/approval-requests/{request_id}/approve", response_model=MessageResponse)
def approve_request(request_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    req = db.get(ApprovalRequest, request_id)
    if not req or req.status != "pending":
        raise HTTPException(status_code=404, detail="pending request not found")

    user = db.get(User, req.user_id)
    if req.request_type == "register":
        user.status = "approved"
    elif req.request_type == "password_change":
        payload = json.loads(req.payload_json)
        user.password_hash = payload["new_password_hash"]
    else:
        raise HTTPException(status_code=400, detail="unknown request type")

    req.status = "approved"
    req.reviewed_by = admin.id
    req.reviewed_at = datetime.utcnow()
    db.commit()
    return {"message": "审批通过"}


@router.post("/approval-requests/{request_id}/reject", response_model=MessageResponse)
def reject_request(request_id: int, db: Session = Depends(get_db), admin: User = Depends(get_admin_user)):
    req = db.get(ApprovalRequest, request_id)
    if not req or req.status != "pending":
        raise HTTPException(status_code=404, detail="pending request not found")

    user = db.get(User, req.user_id)
    if req.request_type == "register":
        user.status = "rejected"

    req.status = "rejected"
    req.reviewed_by = admin.id
    req.reviewed_at = datetime.utcnow()
    db.commit()
    return {"message": "审批驳回"}


@router.post("/seed-admin", response_model=MessageResponse)
def seed_admin(db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.role == "admin").first()
    if exists:
        return {"message": "admin already exists"}
    admin = User(
        email="admin@example.com",
        username="admin",
        password_hash=hash_password("Admin@123456"),
        role="admin",
        status="approved",
    )
    db.add(admin)
    db.commit()
    return {"message": "默认管理员已创建：admin / Admin@123456"}
