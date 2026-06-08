# Skill registry — cache RAM với TTL refresh từ nguồn (MinIO)
import time
import threading
from typing import Callable, Dict, List, Optional
from .base import Skill


class SkillRegistry:
    """Giữ skills trong RAM, tự refresh từ fetch_fn mỗi ttl_seconds.

    fetch_fn() -> list[Skill]: hàm nạp lại toàn bộ skill từ nguồn (MinIO).
    """

    def __init__(self, ttl_seconds: int, fetch_fn: Callable[[], List[Skill]]):
        self._skills: Dict[str, Skill] = {}
        self._ttl = ttl_seconds
        self._fetch_fn = fetch_fn
        self._loaded_at: Optional[float] = None
        self._lock = threading.Lock()

    def _ensure_fresh(self):
        now = time.monotonic()
        if self._loaded_at is not None and (now - self._loaded_at) < self._ttl:
            return
        with self._lock:
            now = time.monotonic()
            if self._loaded_at is not None and (now - self._loaded_at) < self._ttl:
                return
            try:
                skills = self._fetch_fn()
                self._skills = {s.name: s for s in skills}
                print(f"[SKILL] Refreshed {len(self._skills)} skills from MinIO")
            except Exception as e:
                # Giữ cache cũ; vẫn cập nhật mốc để back-off (không hammer khi MinIO down)
                print(f"[SKILL] Refresh failed (giu cache cu): {e}")
            self._loaded_at = now

    def warm(self):
        """Nạp ngay lúc startup (lỗi MinIO không làm sập server)."""
        self._ensure_fresh()

    def get(self, name: str) -> Optional[Skill]:
        self._ensure_fresh()
        return self._skills.get(name)

    def list_all(self) -> List[Skill]:
        self._ensure_fresh()
        return list(self._skills.values())
