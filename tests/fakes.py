from pathlib import Path


class FakeStream:
    def __init__(self, content: bytes):
        self._content = content
        self._offset = 0

    async def read(self, chunk_size: int) -> bytes:
        if self._offset >= len(self._content):
            return b""
        chunk = self._content[self._offset : self._offset + chunk_size]
        self._offset += chunk_size
        return chunk


class FakeS3Client:
    def __init__(self, objects=None, pages=None):
        self.objects = dict(objects or {})
        self.pages = list(pages or [])
        self.deleted_keys = []

    async def list_objects_v2(self, **kwargs):
        if self.pages:
            token = kwargs.get("ContinuationToken")
            if token is None:
                return self.pages[0]

            for page in self.pages:
                if page.get("Token") == token:
                    return page["Response"]

            return {"Contents": [], "IsTruncated": False}

        prefix = kwargs.get("Prefix")
        keys = sorted(self.objects)
        if prefix:
            keys = [key for key in keys if key.startswith(prefix)]

        return {
            "Contents": [{"Key": key} for key in keys],
            "IsTruncated": False,
        }

    async def get_object(self, Bucket, Key):
        return {"Body": FakeStream(self.objects[Key])}

    async def download_file(self, Bucket, Key, Filename):
        path = Path(Filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.objects[Key])

    async def delete_object(self, Bucket, Key):
        self.deleted_keys.append(Key)
        self.objects.pop(Key, None)

    async def upload_file(self, Filename, Bucket, Key):
        self.objects[Key] = Path(Filename).read_bytes()


class FakeClientContext:
    def __init__(self, client):
        self.client = client

    async def __aenter__(self):
        return self.client

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeSession:
    def __init__(self, client):
        self._client = client

    def client(self, service_name):
        assert service_name == "s3"
        return FakeClientContext(self._client)
