import json
import tempfile
import unittest
from pathlib import Path

from tc.runtime.raw_sink import FileRawSink, RawPersistenceError


class FileRawSinkTests(unittest.TestCase):
    def test_preserves_native_json_and_refuses_overwrite(self):
        response = {
            "status": "completed",
            "exchange": "OANDA",
            "symbol": "XAUUSD",
            "interval": "1h",
            "analysis": "{\"x\":1}",
            "unknown": {"keep": True},
        }
        with tempfile.TemporaryDirectory() as tmp:
            sink = FileRawSink(tmp)
            uri = sink.preserve(
                source_run_id="run-1",
                execution_order=1,
                native_response=response,
            )
            path = Path(uri.removeprefix("file://"))
            with path.open("r", encoding="utf-8") as handle:
                stored = json.load(handle)
            self.assertEqual(stored, response)

            with self.assertRaises(RawPersistenceError):
                sink.preserve(
                    source_run_id="run-1",
                    execution_order=1,
                    native_response=response,
                )


if __name__ == "__main__":
    unittest.main()
