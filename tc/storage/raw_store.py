from __future__ import annotations

import copy
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from tc.native.client import NativeRequest

_ARTIFACT_SCHEME = "tcraw"
_ARTIFACT_AUTHORITY = "v1"
_SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class RawStorageError(Exception):
    """Base class for durable Raw Storage failures."""


class InvalidRawStorageInputError(RawStorageError, ValueError):
    """Raised when a request or logical artifact reference is unsafe/invalid."""


class DuplicateRawArtifactError(RawStorageError, FileExistsError):
    """Raised when a logical Raw artifact already exists."""


class RawStoragePublicationError(RawStorageError, OSError):
    """Raised when a fully written temporary artifact cannot be published."""


class RawStorageVerificationError(RawStorageError):
    """Raised when durable read-back differs from the requested Native response."""


def _validate_run_id(source_run_id: str) -> None:
    if not isinstance(source_run_id, str) or not _SAFE_RUN_ID.fullmatch(source_run_id):
        raise InvalidRawStorageInputError(
            "source_run_id must match [A-Za-z0-9][A-Za-z0-9._-]{0,127}"
        )


def _order_token(execution_order: int) -> str:
    if isinstance(execution_order, bool) or not isinstance(execution_order, int):
        raise InvalidRawStorageInputError("execution_order must be an integer")
    if execution_order < 1:
        raise InvalidRawStorageInputError("execution_order must be >= 1")
    return f"{execution_order:02d}"


def build_source_raw_artifact(source_run_id: str, execution_order: int) -> str:
    """Return the stable logical TC-P3 Raw artifact reference."""

    _validate_run_id(source_run_id)
    token = _order_token(execution_order)
    return f"{_ARTIFACT_SCHEME}://{_ARTIFACT_AUTHORITY}/{source_run_id}/{token}.json"


class FileRawStorage:
    """Durable filesystem implementation of the TC-P2 RawPreserver protocol.

    The stored file contains only the untouched Native response at the semantic
    JSON-value level. Publication is no-overwrite and atomic at the final-name
    boundary: POSIX uses hard-link publication from a fully fsynced same-directory
    temporary file; Windows uses same-directory os.rename(), whose destination
    creation fails when the final path already exists.
    """

    def __init__(self, root: str | os.PathLike[str]) -> None:
        root_path = Path(root).expanduser()
        try:
            root_path.mkdir(parents=True, exist_ok=True)
            if not root_path.is_dir():
                raise NotADirectoryError(str(root_path))
            self._root = root_path.resolve()
        except OSError as exc:
            raise RawStoragePublicationError(
                f"storage root unavailable: {root_path}"
            ) from exc

    @property
    def root(self) -> Path:
        return self._root

    def preserve(
        self,
        *,
        request: NativeRequest,
        original_response: Mapping[str, Any],
    ) -> str:
        """Persist one Native response without overwrite and return its logical ref."""

        if not isinstance(request, NativeRequest):
            raise InvalidRawStorageInputError("request must be NativeRequest")
        _validate_run_id(request.source_run_id)
        token = _order_token(request.execution_order)
        if not isinstance(original_response, Mapping) or not original_response:
            raise InvalidRawStorageInputError(
                "original_response must be a non-empty mapping"
            )

        snapshot = copy.deepcopy(dict(original_response))
        try:
            serialized = json.dumps(
                snapshot,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            )
            serialized_bytes = serialized.encode("utf-8")
            decoded = json.loads(serialized_bytes.decode("utf-8"))
        except (TypeError, ValueError, UnicodeError) as exc:
            raise InvalidRawStorageInputError(
                "original_response must be losslessly JSON serializable"
            ) from exc
        if decoded != snapshot:
            raise InvalidRawStorageInputError(
                "JSON serialization would change original_response values"
            )
        if "analysis" in snapshot and decoded.get("analysis") != snapshot["analysis"]:
            raise InvalidRawStorageInputError(
                "analysis string would not round-trip exactly"
            )

        parent = self._root / _ARTIFACT_AUTHORITY / request.source_run_id
        final_path = parent / f"{token}.json"
        try:
            parent.mkdir(parents=True, exist_ok=True)
            resolved_parent = parent.resolve()
        except OSError as exc:
            raise RawStoragePublicationError(
                f"cannot prepare artifact directory for {request.source_run_id}"
            ) from exc

        if self._root not in (resolved_parent, *resolved_parent.parents):
            raise InvalidRawStorageInputError("resolved artifact path escapes storage root")

        temp_path: Path | None = None
        published = False
        try:
            fd, temp_name = tempfile.mkstemp(
                prefix=".tcraw-",
                suffix=".tmp",
                dir=resolved_parent,
            )
            temp_path = Path(temp_name)
            with os.fdopen(fd, "wb") as handle:
                handle.write(serialized_bytes)
                handle.flush()
                os.fsync(handle.fileno())

            self._verify_path(temp_path, snapshot)
            self._publish_no_overwrite(temp_path, final_path)
            published = True
            self._fsync_directory(resolved_parent)
            self._verify_path(final_path, snapshot)
        except DuplicateRawArtifactError:
            raise
        except RawStorageError:
            raise
        except FileExistsError as exc:
            raise DuplicateRawArtifactError(
                f"raw artifact already exists: {final_path.name}"
            ) from exc
        except OSError as exc:
            raise RawStoragePublicationError(
                f"raw artifact publication failed: {final_path.name}"
            ) from exc
        finally:
            if temp_path is not None and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

        if not published:
            raise RawStoragePublicationError("raw artifact was not published")
        return build_source_raw_artifact(
            request.source_run_id, request.execution_order
        )

    def read(self, source_raw_artifact: str) -> dict[str, Any]:
        path = self._path_from_reference(source_raw_artifact)
        try:
            raw_bytes = path.read_bytes()
            loaded = json.loads(raw_bytes.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise RawStorageVerificationError(
                f"cannot read raw artifact: {source_raw_artifact}"
            ) from exc
        if not isinstance(loaded, dict):
            raise RawStorageVerificationError(
                "stored raw artifact root must be an object"
            )
        return loaded

    def _path_from_reference(self, source_raw_artifact: str) -> Path:
        if not isinstance(source_raw_artifact, str) or not source_raw_artifact:
            raise InvalidRawStorageInputError(
                "source_raw_artifact must be a non-empty string"
            )
        parsed = urlparse(source_raw_artifact)
        if (
            parsed.scheme != _ARTIFACT_SCHEME
            or parsed.netloc != _ARTIFACT_AUTHORITY
            or parsed.params
            or parsed.query
            or parsed.fragment
        ):
            raise InvalidRawStorageInputError("unsupported raw artifact reference")
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) != 2:
            raise InvalidRawStorageInputError("invalid raw artifact reference path")
        source_run_id, filename = parts
        _validate_run_id(source_run_id)
        if not re.fullmatch(r"[0-9]+\.json", filename):
            raise InvalidRawStorageInputError("invalid raw artifact filename")
        path = self._root / _ARTIFACT_AUTHORITY / source_run_id / filename
        resolved_parent = path.parent.resolve()
        if self._root not in (resolved_parent, *resolved_parent.parents):
            raise InvalidRawStorageInputError("resolved artifact path escapes storage root")
        return path

    @staticmethod
    def _verify_path(path: Path, expected: Mapping[str, Any]) -> None:
        try:
            raw_bytes = path.read_bytes()
            decoded = json.loads(raw_bytes.decode("utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise RawStorageVerificationError(
                f"raw artifact read-back failed: {path.name}"
            ) from exc
        if decoded != expected:
            raise RawStorageVerificationError(
                f"raw artifact read-back mismatch: {path.name}"
            )
        if "analysis" in expected and decoded.get("analysis") != expected["analysis"]:
            raise RawStorageVerificationError(
                f"analysis string read-back mismatch: {path.name}"
            )

    @staticmethod
    def _publish_no_overwrite(temp_path: Path, final_path: Path) -> None:
        if os.name == "nt":
            try:
                os.rename(temp_path, final_path)
            except FileExistsError as exc:
                raise DuplicateRawArtifactError(
                    f"raw artifact already exists: {final_path.name}"
                ) from exc
            return

        try:
            os.link(temp_path, final_path)
        except FileExistsError as exc:
            raise DuplicateRawArtifactError(
                f"raw artifact already exists: {final_path.name}"
            ) from exc

    @staticmethod
    def _fsync_directory(directory: Path) -> None:
        flags = getattr(os, "O_DIRECTORY", 0)
        if not flags:
            return
        try:
            fd = os.open(directory, os.O_RDONLY | flags)
        except OSError as exc:
            raise RawStoragePublicationError(
                f"cannot open artifact directory for fsync: {directory}"
            ) from exc
        try:
            os.fsync(fd)
        except OSError as exc:
            raise RawStoragePublicationError(
                f"cannot fsync artifact directory: {directory}"
            ) from exc
        finally:
            os.close(fd)
