import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_approved_user
from app.db.session import get_db
from app.models.audio import AudioTrack
from app.models.document import Document
from app.models.user import User
from app.schemas.audio import TTSRequest, TTSResponse
from app.services.audio_service import AudioService

router = APIRouter(prefix="/audio", tags=["audio"])
service = AudioService()


@router.post("/tts", response_model=TTSResponse)
def synthesize_audio(
    payload: TTSRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_approved_user),
):
    document = db.get(Document, payload.document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="document not found")
    try:
        track = service.create_audio(db, payload.document_id, payload.speed, payload.voice, payload.return_word_marks)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "audio_track_id": track.id,
        "audio_url": track.audio_url,
        "speed": float(track.speed),
        "sync_marks": json.loads(track.marks_json),
    }


@router.get("/tracks/{track_id}", response_model=TTSResponse)
def get_audio_track(track_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_approved_user)):
    track = db.get(AudioTrack, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="track not found")
    document = db.get(Document, track.document_id)
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    return {
        "audio_track_id": track.id,
        "audio_url": track.audio_url,
        "speed": float(track.speed),
        "sync_marks": json.loads(track.marks_json),
    }
