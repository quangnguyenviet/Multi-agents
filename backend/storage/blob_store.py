# Blob store tạm cho file bytes (PDF/Word). Backend: in-memory (dev) hoặc Redis (production).
# Interface dict-like để chỗ dùng không phải đổi: store[k]=v, store.get(k), store.pop(k, d), k in store
from config.settings import settings


class _MemoryBlobStore:
    """Lưu trong RAM (dev). Không TTL, mất khi restart, không share đa worker."""

    def __init__(self):
        self._d = {}

    def __setitem__(self, key, value):
        self._d[key] = value

    def __getitem__(self, key):
        return self._d[key]

    def get(self, key, default=None):
        return self._d.get(key, default)

    def pop(self, key, default=None):
        return self._d.pop(key, default)

    def __contains__(self, key):
        return key in self._d


class _RedisBlobStore:
    """Lưu trên Redis (production): bytes + TTL, share giữa các worker."""

    def __init__(self, url: str, prefix: str, ttl: int):
        import redis  # lazy import
        self._r = redis.Redis.from_url(url)
        self._prefix = prefix
        self._ttl = ttl

    def _k(self, key) -> str:
        return f"{self._prefix}:{key}"

    def __setitem__(self, key, value):
        self._r.set(self._k(key), value, ex=self._ttl)

    def __getitem__(self, key):
        value = self._r.get(self._k(key))
        if value is None:
            raise KeyError(key)
        return value

    def get(self, key, default=None):
        value = self._r.get(self._k(key))
        return value if value is not None else default

    def pop(self, key, default=None):
        k = self._k(key)
        value = self._r.get(k)
        self._r.delete(k)
        return value if value is not None else default

    def __contains__(self, key):
        return self._r.exists(self._k(key)) > 0


def make_blob_store(prefix: str):
    """Chọn backend theo cấu hình: có REDIS_URL → Redis, ngược lại → in-memory."""
    if settings.REDIS_URL:
        return _RedisBlobStore(settings.REDIS_URL, prefix, settings.BLOB_TTL)
    return _MemoryBlobStore()
