import asyncio

import click
import pytest

from tests.fakes import FakeS3Client, FakeSession


def test_upload_and_list_files(s3_manager, fake_s3_client, tmp_path):
    file_path = tmp_path / "example.txt"
    file_path.write_text("hello")

    uploaded_key = asyncio.run(s3_manager.upload_file(str(file_path), "example.txt"))
    files = asyncio.run(s3_manager.list_all_files())

    assert uploaded_key == "example.txt"
    assert files == ["example.txt"]
    assert fake_s3_client.objects["example.txt"] == b"hello"


def test_list_all_files_uses_pagination(monkeypatch):
    from s3 import service as s3_service

    paginated_client = FakeS3Client(
        pages=[
            {
                "Contents": [{"Key": "a.txt"}],
                "IsTruncated": True,
                "NextContinuationToken": "page-2",
            },
            {
                "Token": "page-2",
                "Response": {
                    "Contents": [{"Key": "b.txt"}],
                    "IsTruncated": False,
                },
            },
        ]
    )
    settings = type(
        "Settings",
        (),
        {"aws": type("AWS", (), {"bucket_name": "test-bucket"})()},
    )()

    monkeypatch.setattr(s3_service, "get_settings", lambda: settings)
    monkeypatch.setattr(s3_service, "get_s3_session", lambda: FakeSession(paginated_client))

    manager = s3_service.S3BucketManager()

    files = asyncio.run(manager.list_all_files())

    assert files == ["a.txt", "b.txt"]


def test_search_filters_matching_suffixes(s3_manager, fake_s3_client):
    fake_s3_client.objects.update(
        {
            "reports/january.csv": b"january",
            "reports/february.csv": b"february",
            "logs/january.log": b"log",
        }
    )

    matches = asyncio.run(s3_manager.search_for_file("january.csv"))

    assert matches == ["reports/january.csv"]


def test_stream_file_returns_content_in_chunks(s3_manager, fake_s3_client):
    fake_s3_client.objects["chunked.txt"] = b"abcdef"

    async def collect_chunks():
        return [chunk async for chunk in s3_manager.stream_file("chunked.txt", chunk_size=2)]

    chunks = asyncio.run(collect_chunks())

    assert chunks == [b"ab", b"cd", b"ef"]


def test_download_file_uses_key_name_by_default(s3_manager, fake_s3_client, monkeypatch, tmp_path):
    fake_s3_client.objects["folder/report.txt"] = b"payload"
    monkeypatch.chdir(tmp_path)

    local_path = asyncio.run(s3_manager.download_file("folder/report.txt"))

    assert local_path == "report.txt"
    assert (tmp_path / "report.txt").read_bytes() == b"payload"


def test_download_file_uses_destination_directory(s3_manager, fake_s3_client, tmp_path):
    fake_s3_client.objects["folder/report.txt"] = b"payload"
    destination = tmp_path / "downloads"
    destination.mkdir()

    local_path = asyncio.run(s3_manager.download_file("folder/report.txt", destination))

    assert local_path == str(destination / "report.txt")
    assert (destination / "report.txt").read_bytes() == b"payload"


def test_delete_file_removes_object(s3_manager, fake_s3_client):
    fake_s3_client.objects["old.txt"] = b"delete me"

    deleted = asyncio.run(s3_manager.delete_file("old.txt"))

    assert deleted is True
    assert "old.txt" not in fake_s3_client.objects
    assert fake_s3_client.deleted_keys == ["old.txt"]


def test_upload_files_parallel_uploads_all_files(s3_manager, fake_s3_client, tmp_path):
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("one")
    second.write_text("two")

    asyncio.run(
        s3_manager.upload_files_parallel(
            [
                (str(first), "files/first.txt"),
                (str(second), "files/second.txt"),
            ]
        )
    )

    assert fake_s3_client.objects == {
        "files/first.txt": b"one",
        "files/second.txt": b"two",
    }


def test_download_files_parallel_downloads_all_files(s3_manager, fake_s3_client, tmp_path):
    fake_s3_client.objects.update(
        {
            "files/first.txt": b"one",
            "files/second.txt": b"two",
        }
    )

    asyncio.run(
        s3_manager.download_files_parallel(
            ["files/first.txt", "files/second.txt"],
            str(tmp_path),
        )
    )

    assert (tmp_path / "first.txt").read_bytes() == b"one"
    assert (tmp_path / "second.txt").read_bytes() == b"two"


def test_init_requires_bucket(monkeypatch):
    from s3 import service as s3_service

    settings = type(
        "Settings",
        (),
        {"aws": type("AWS", (), {"bucket_name": None})()},
    )()

    monkeypatch.setattr(s3_service, "get_settings", lambda: settings)
    monkeypatch.setattr(s3_service, "get_s3_session", lambda: FakeSession(FakeS3Client()))

    with pytest.raises(click.UsageError, match="Missing bucket"):
        s3_service.S3BucketManager()
