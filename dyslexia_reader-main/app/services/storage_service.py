from pathlib import Path
import shutil
import uuid


class LocalStorageService:
    def __init__(self, base_dir: str = "storage\\image"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, source_file, original_filename: str) -> str:
        suffix = Path(original_filename).suffix
        filename = f"{uuid.uuid4().hex}{suffix}"
        target = self.base_dir / filename
        with open(target, "wb") as out:
            shutil.copyfileobj(source_file, out)
        return str(target)

    def save_bytes(self, content: bytes, filename: str) -> str:
        safe_name = f"{uuid.uuid4().hex}_{filename}"
        target = self.base_dir / safe_name
        with open(target, "wb") as out:
            out.write(content)
        return str(target)