# storage.py
import os
import json
import tempfile
import datetime
import uuid
from typing import List, Dict, Any, Optional

def get_storage_path(filename="tasks.json") -> str:
    return os.path.join(os.path.dirname(__file__), filename)

def atomic_write_json(path: str, data: Any) -> None:
    dirpath = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        # ensure temp file cleaned up on error
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise

def load_tasks(path: Optional[str] = None) -> List[Dict]:
    if path is None:
        path = get_storage_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks: List[Dict], path: Optional[str] = None) -> None:
    if path is None:
        path = get_storage_path()
    atomic_write_json(path, tasks)

def make_task(text: str, due_date: Optional[str] = None) -> Dict:
    return {
        "id": uuid.uuid4().hex,
        "task": text.strip(),
        "created_at": datetime.datetime.now().isoformat(),
        "due_date": due_date,
    }

def migrate_pickle_to_json(old_path: str = "tasks.pkl", new_path: str | None = None) -> int:
    """
    If a pickle file exists (older app versions), convert it to JSON (new format).
    Returns number of migrated tasks.
    """
    import pickle
    if new_path is None:
        new_path = get_storage_path()
    if not os.path.exists(old_path):
        return 0
    try:
        with open(old_path, "rb") as f:
            tasks = pickle.load(f)
    except Exception:
        # if pickle is corrupt/untrusted, skip migration
        return 0

    # normalize tasks (ensure id and created_at are strings)
    normalized = []
    for t in tasks:
        if isinstance(t, dict):
            normalized.append({
                "id": t.get("id") or uuid.uuid4().hex,
                "task": str(t.get("task", "")),
                "created_at": getattr(t.get("created_at"), "isoformat", lambda: str(t.get("created_at")))(),
                "due_date": t.get("due_date") if t.get("due_date") is not None else None,
            })
    save_tasks(normalized, path=new_path)
    return len(normalized)