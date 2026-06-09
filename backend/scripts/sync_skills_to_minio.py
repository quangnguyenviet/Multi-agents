"""Sync các file skill seed (skills/library/*.md) lên bucket MinIO.

Dùng cho migration lần đầu và mỗi khi sửa seed trong repo.
Chạy từ thư mục backend/:  python scripts/sync_skills_to_minio.py
"""
import os
import sys

# Cho phép import config/storage khi chạy trực tiếp từ scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from minio import Minio
from core.settings import settings

SEED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "skills", "library")


def main():
    client = Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )

    bucket = settings.MINIO_BUCKET_SKILLS
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        print(f"[SYNC] Created bucket: {bucket}")
    else:
        print(f"[SYNC] Bucket exists: {bucket}")

    if not os.path.isdir(SEED_DIR):
        print(f"[SYNC] Seed dir khong ton tai: {SEED_DIR}")
        return

    count = 0
    for filename in os.listdir(SEED_DIR):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(SEED_DIR, filename)
        client.fput_object(bucket, filename, filepath, content_type="text/markdown")
        print(f"[SYNC] Uploaded: {filename}")
        count += 1

    print(f"[SYNC] Done. {count} skill(s) -> minio://{bucket}")


if __name__ == "__main__":
    main()
