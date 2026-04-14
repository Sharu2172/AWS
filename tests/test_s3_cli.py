from click.testing import CliRunner

from s3.cli import s3


class FakeManager:
    def __init__(self, bucket):
        self.bucket = bucket

    async def list_all_files(self):
        return ["alpha.txt", "beta.txt"]

    async def stream_file(self, key):
        yield f"contents:{key}".encode("utf-8")

    async def upload_file(self, file, key):
        self.upload_args = (file, key)

    async def delete_file(self, key):
        self.deleted_key = key

    async def upload_files_parallel(self, files):
        self.upload_many_files = files

    async def download_files_parallel(self, keys, dest):
        self.download_many_args = (keys, dest)

    async def search_for_file(self, prefix):
        return [f"{prefix}-match.txt"]


def test_list_command_prints_files(monkeypatch):
    monkeypatch.setattr("s3.cli.S3BucketManager", FakeManager)

    result = CliRunner().invoke(s3, ["list", "--bucket", "demo-bucket"])

    assert result.exit_code == 0
    assert result.output == "alpha.txt\nbeta.txt\n"


def test_read_command_prints_stream_contents(monkeypatch):
    monkeypatch.setattr("s3.cli.S3BucketManager", FakeManager)

    result = CliRunner().invoke(s3, ["read", "--bucket", "demo-bucket", "--key", "notes.txt"])

    assert result.exit_code == 0
    assert result.output == "contents:notes.txt"


def test_upload_many_rejects_invalid_entries(monkeypatch):
    monkeypatch.setattr("s3.cli.S3BucketManager", FakeManager)

    result = CliRunner().invoke(s3, ["upload-many", "--bucket", "demo-bucket", "--files", "bad-format"])

    assert result.exit_code != 0
    assert "Each --files entry must use the format local:key" in result.output


def test_search_command_prints_matches(monkeypatch):
    monkeypatch.setattr("s3.cli.S3BucketManager", FakeManager)

    result = CliRunner().invoke(s3, ["search", "--bucket", "demo-bucket", "--prefix", "invoice"])

    assert result.exit_code == 0
    assert result.output == "invoice-match.txt\n"
