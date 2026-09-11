from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tc.adapter.adapter import TCAdapter
from tc.native.client import NativeClient, NativeRequest
from tc.storage import (
    DuplicateRawArtifactError,
    FileRawStorage,
    InvalidRawStorageInputError,
    RawStoragePublicationError,
    build_source_raw_artifact,
)


def make_request(
    *,
    request_id: str = "REQ-003",
    source_run_id: str = "RUN-001",
    execution_order: int = 3,
) -> NativeRequest:
    return NativeRequest(
        request_id=request_id,
        source_run_id=source_run_id,
        execution_order=execution_order,
        analysis_source="OANDA",
        analysis_symbol="XAUUSD",
        timeframe="H1",
    )


def make_response() -> dict:
    analysis = (
        '{"observations":"Wait\\n確認 ✓","potentialPosition":'
        '{"positionType":"long","entryPrice":4428.296,'
        '"stopLoss":4405.199,"takeProfits":[4445,4460,4480]},'
        '"action_url":"https://example.invalid/chart?chartId=chart-123",'
        '"unknownInner":{"keep":[1,true,null]}}'
    )
    return {
        "status": "completed",
        "exchange": "OANDA",
        "symbol": "XAUUSD",
        "interval": "1h",
        "analysis": analysis,
        "model": "native-model",
        "timestamp": "2026-09-10T10:14:36.173Z",
        "unknownOuter": {"日本語": "保持", "nested": [1, {"x": True}]},
    }


class RecordingExecutor:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.calls = []

    def __call__(self, *, exchange, symbol, interval):
        self.calls.append((exchange, symbol, interval))
        return copy.deepcopy(self.payload)


class FileRawStorageTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "raw-store"
        self.storage = FileRawStorage(self.root)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_preserve_read_roundtrip_and_exact_analysis_string(self):
        request = make_request()
        payload = make_response()
        ref = self.storage.preserve(request=request, original_response=payload)

        self.assertEqual(ref, "tcraw://v1/RUN-001/03.json")
        loaded = self.storage.read(ref)
        self.assertEqual(loaded, payload)
        self.assertEqual(loaded["analysis"], payload["analysis"])
        self.assertEqual(loaded["unknownOuter"], payload["unknownOuter"])

        path = self.root / "v1" / "RUN-001" / "03.json"
        self.assertTrue(path.is_file())
        self.assertFalse(any(path.parent.glob(".tcraw-*.tmp")))

    def test_duplicate_logical_artifact_is_never_overwritten(self):
        request = make_request()
        first = make_response()
        second = make_response()
        second["status"] = "changed"

        ref = self.storage.preserve(request=request, original_response=first)
        with self.assertRaises(DuplicateRawArtifactError):
            self.storage.preserve(request=request, original_response=second)

        self.assertEqual(self.storage.read(ref), first)

    def test_repeat_execution_orders_are_independent_artifacts(self):
        payload = make_response()
        ref3 = self.storage.preserve(
            request=make_request(request_id="REQ-003", execution_order=3),
            original_response=payload,
        )
        ref4 = self.storage.preserve(
            request=make_request(request_id="REQ-004", execution_order=4),
            original_response=payload,
        )
        self.assertEqual(ref3, "tcraw://v1/RUN-001/03.json")
        self.assertEqual(ref4, "tcraw://v1/RUN-001/04.json")
        self.assertNotEqual(ref3, ref4)
        self.assertEqual(self.storage.read(ref3), payload)
        self.assertEqual(self.storage.read(ref4), payload)

    def test_path_traversal_like_run_id_is_rejected(self):
        request = make_request(source_run_id="../escape")
        with self.assertRaises(InvalidRawStorageInputError):
            self.storage.preserve(request=request, original_response=make_response())
        self.assertFalse((Path(self.tempdir.name) / "escape").exists())

    def test_reference_parser_rejects_wrong_scheme_or_traversal_shape(self):
        for ref in (
            "file:///tmp/raw.json",
            "tcraw://v1/../03.json",
            "tcraw://v2/RUN-001/03.json",
            "tcraw://v1/RUN-001/not-number.json",
        ):
            with self.subTest(ref=ref):
                with self.assertRaises(InvalidRawStorageInputError):
                    self.storage.read(ref)

    def test_non_json_or_lossy_mapping_is_rejected_before_publication(self):
        payload = make_response()
        payload["bad"] = float("nan")
        with self.assertRaises(InvalidRawStorageInputError):
            self.storage.preserve(
                request=make_request(), original_response=payload
            )
        self.assertFalse((self.root / "v1" / "RUN-001" / "03.json").exists())

    def test_publication_failure_leaves_no_authoritative_final_or_temp(self):
        payload = make_response()
        with mock.patch("tc.storage.raw_store.os.link", side_effect=OSError("link fail")):
            with self.assertRaises(RawStoragePublicationError):
                self.storage.preserve(
                    request=make_request(), original_response=payload
                )
        parent = self.root / "v1" / "RUN-001"
        self.assertFalse((parent / "03.json").exists())
        self.assertFalse(any(parent.glob(".tcraw-*.tmp")))

    def test_unusable_root_fails_explicitly(self):
        file_root = Path(self.tempdir.name) / "not-a-dir"
        file_root.write_text("x", encoding="utf-8")
        with self.assertRaises(RawStoragePublicationError):
            FileRawStorage(file_root)

    def test_adapter_with_concrete_storage_preserves_before_raw_output(self):
        payload = make_response()
        executor = RecordingExecutor(payload)
        adapter = TCAdapter(NativeClient(executor), self.storage)
        raw_record = adapter.analyze(make_request()).raw_record

        ref = raw_record["record_identity"]["source_raw_artifact"]
        self.assertEqual(ref, "tcraw://v1/RUN-001/03.json")
        self.assertEqual(self.storage.read(ref), payload)
        self.assertEqual(raw_record["original_response"], payload)
        self.assertEqual(raw_record["original_response"]["analysis"], payload["analysis"])
        self.assertEqual(raw_record["parse_status"], {"state": "PARSED"})
        self.assertEqual(
            raw_record["derived_metadata"]["chart_id"]["value"], "chart-123"
        )

    def test_reference_builder_matches_storage_convention(self):
        self.assertEqual(
            build_source_raw_artifact("RUN-ABC_01", 12),
            "tcraw://v1/RUN-ABC_01/12.json",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
