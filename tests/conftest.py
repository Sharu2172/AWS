from types import SimpleNamespace

import pytest

from tests.fakes import FakeS3Client, FakeSession


@pytest.fixture
def fake_s3_client():
    return FakeS3Client()


@pytest.fixture
def s3_manager(monkeypatch, fake_s3_client):
    from s3 import service as s3_service

    settings = SimpleNamespace(
        aws=SimpleNamespace(bucket_name="test-bucket", region="ap-south-1")
    )

    monkeypatch.setattr(s3_service, "get_settings", lambda: settings)
    monkeypatch.setattr(s3_service, "get_s3_session", lambda: FakeSession(fake_s3_client))

    return s3_service.S3BucketManager()
