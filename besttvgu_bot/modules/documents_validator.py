import hashlib
from functools import wraps
from json import dumps, loads
from pathlib import Path

import aiofiles
from aiofiles import os
from pydantic import BaseModel


# Все документы в формате PDF


class DocumentInfo(BaseModel):
    name: str
    filename: str
    version: str

    model_config = {"frozen": True}


class UserConsents(BaseModel):
    policy: DocumentInfo
    agreement: DocumentInfo

    model_config = {"frozen": True}


class NotInitializedError(RuntimeError):
    pass


class DocumentNeedsVersionUpdate(Exception):
    pass


def require_initialized(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not getattr(self, "is_initialized", False):
            raise NotInitializedError(
                f"{self.__class__.__name__} must be initialized before calling {method.__name__}"
            )
        return method(self, *args, **kwargs)

    return wrapper


def get_document_name(document_version: str, document_name: str) -> str:
    return f"{document_name}_{document_version}.pdf"


class DocumentsHandler:
    def __init__(
            self,
            documents_hashes_file_path: Path,
            documents_path: Path,
            documents: dict[str, DocumentInfo]
    ) -> None:
        self.is_initialized: bool = False

        self.documents_hashes_file_path: Path = documents_hashes_file_path
        self.documents_dir: Path = documents_path
        self.documents: dict[str, DocumentInfo] = documents

        self.documents_fullnames: dict[str, str] | None = None
        self.documents_paths: dict[str, Path] | None = None
        self.documents_hashes: dict[str, str] | None = None

    async def init(self) -> None:
        if not self.documents_dir.exists():
            await os.makedirs(self.documents_dir, exist_ok=True)

        if not self.documents_hashes_file_path.exists():
            await self.save_documents_hashes({})

        self.documents_hashes = await self.get_cur_documents_hashes()

        self.is_initialized = True

        await self.save_documents_hashes(self.documents_hashes)

    async def save_documents_hashes(self, document_hashes: dict[str, str]) -> None:
        async with aiofiles.open(self.documents_hashes_file_path, "w+", encoding="UTF-8") as f:
            await f.write(dumps(document_hashes, ensure_ascii=False, indent=4))

    async def get_cur_documents_hashes(self) -> dict[str, str]:
        if not self.documents_hashes_file_path.exists():
            raise FileNotFoundError(f"No such documents hashes file: {self.documents_hashes_file_path}")

        async with aiofiles.open(self.documents_hashes_file_path, "r", encoding="UTF-8") as f:
            return loads(await f.read())

    @require_initialized
    async def handle_documents(self):
        self.documents_fullnames = {}
        self.documents_paths = {}

        for document_name, document in self.documents.items():
            await self.update_actuality_document(document_name, document)

            self.documents_fullnames[document_name] = get_document_name(document.version, document.filename)
            self.documents_paths[document_name] = self.get_document_path(document.version, document.filename)

    @require_initialized
    def get_document_path(self, document_version: str, document_name: str) -> Path:
        return self.documents_dir / get_document_name(document_version, document_name)

    @require_initialized
    async def get_document_file_bytes(self, document_version: str, document_name: str) -> bytes:
        file_path: Path = self.get_document_path(document_version, document_name)

        if not file_path.exists():
            raise FileNotFoundError(f"No such document: {file_path}")

        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()

    @require_initialized
    async def update_actuality_document(self, document_name: str, document: DocumentInfo) -> None:
        filename: str = get_document_name(document.version, document.filename)
        file_bytes: bytes = await self.get_document_file_bytes(document.version, document.filename)

        file_hash: str = hashlib.sha256(file_bytes).hexdigest()

        if self.documents_hashes.get(filename) is None:
            self.documents_hashes[filename] = file_hash
        else:
            if self.documents_hashes[filename] != file_hash:
                raise DocumentNeedsVersionUpdate(
                    f"❌  Need to update a document \"{document_name}\""
                    f" (from {self.documents_hashes[filename]} to {file_hash})"
                )

    @require_initialized
    def get_document_hash(self, document_name: str) -> str:
        if self.documents_fullnames.get(document_name) is None:
            raise KeyError(f"No such document: {document_name}")

        return self.documents_hashes[self.documents_fullnames[document_name]]

    @require_initialized
    def get_document_fullname(self, document_name: str) -> str:
        if self.documents_fullnames.get(document_name) is None:
            raise KeyError(f"No such document: {document_name}")

        return self.documents_fullnames[document_name]

    @require_initialized
    def get_document_path_by_name(self, document_name: str) -> Path:
        if self.documents_paths.get(document_name) is None:
            raise KeyError(f"No such document: {document_name}")

        return self.documents_paths[document_name]

    @require_initialized
    async def get_document_bytes_by_name(self, document_name: str) -> Path:
        if self.documents_fullnames.get(document_name) is None:
            raise KeyError(f"No such document: {document_name}")

        document: DocumentInfo = self.documents[document_name]
        return await self.get_document_file_bytes(document.version, document.filename)
