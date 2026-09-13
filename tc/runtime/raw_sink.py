from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping


class RawPersistenceError(RuntimeError):
    pass


class FileRawSink:
    """Persist Native responses as immutable per-run JSON artifacts.

    This sink preserves the semantic JSON values returned by the Native Client.
    It never overwrites an existing artifact. Atomic replace is used only to
    publish a newly-created temporary file into a previously absent final path.
    """

    def __init__(self, root: str | os.PathLike[str]):
        self.root = Path(root)

    def preserve(
        self,
        *,
        source_run_id: str,
        execution_order: int,
        native_response: Mapping[str, Any],
    ) -> str:
        if not source_run_id:
            raise RawPersistenceError("source_run_id is required")
        if execution_order < 1:
            raise RawPersistenceError("execution_order must be >= 1")
        if not isinstance(native_response, Mapping) or not native_response:
            raise RawPersistenceError("native_response must be a non-empty mapping")

        safe_run_id = source_run_id.replace("/", "_").replace("\\", "_")
        run_dir = self.root / safe_run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        final_path = run_dir / f"{execution_order:02d}_native.json"
        if final_path.exists():
            raise RawPersistenceError(f"raw artifact already exists: {final_path}")

        temp_path = run_dir / f".{execution_order:02d}_native.json.tmp"
        if temp_path.exists():
            temp_path.unlink()

        try:
            with temp_path.open("x", encoding="utf-8", newline="\n") as handle:
                json.dump(
                    dict(native_response),
                    handle,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())

            # Refuse overwrite even in a race. os.link creates the final path
            # only when absent; the temporary artifact is then removed.
            os.link(temp_path, final_path)
            temp_path.unlink()
        except FileExistsError as exc:
            if temp_path.exists():
                temp_path.unlink()
            raise RawPersistenceError(f"raw artifact already exists: {final_path}") from exc
        except Exception as exc:
            if temp_path.exists():
                temp_path.unlink()
            raise RawPersistenceError(f"failed to preserve raw artifact: {exc}") from exc

        return final_path.resolve().as_uri()
