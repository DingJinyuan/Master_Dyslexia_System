import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_approved_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.approval import ApprovalRequest
from app.models.user import User
from app.schemas.auth import MessageResponse, PasswordChangeRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=MessageResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    exists = db.query(User).filter(
        (User.email == payload.email) | (User.username == payload.username)
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="email or username already exists")

    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        role="user",
        status="pending",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    req = ApprovalRequest(
        user_id=user.id,
        request_type="register",
        payload_json=json.dumps(payload.model_dump(exclude={"password"}), ensure_ascii=False),
        status="pending",
    )
    db.add(req)
    db.commit()
    return {"message": "注册申请已提交，需管理员审批后方可登录"}


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    username_or_email = form_data.username
    password = form_data.password

    user = db.query(User).filter(
        ((User.username == username_or_email) | (User.email == username_or_email))
    ).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    if user.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号尚未审批通过"
        )

    access_token = create_access_token(str(user.id))
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/password-change-request", response_model=MessageResponse)
def request_password_change(
    payload: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="old password is incorrect")

    req = ApprovalRequest(
        user_id=current_user.id,
        request_type="password_change",
        payload_json=json.dumps(
            {"new_password_hash": hash_password(payload.new_password)},
            ensure_ascii=False
        ),
        status="pending",
    )
    db.add(req)
    db.commit()
    return {"message": "修改密码申请已提交，需管理员审批"}
