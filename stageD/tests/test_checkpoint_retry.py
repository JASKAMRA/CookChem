from __future__ import annotations

import unittest
import sys
from pathlib import Path

STAGE_D = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STAGE_D / "src"))
from stage_d.checkpoint_retry import RetryingCheckpointProvider  # noqa: E402


class FlakyCheckpointProvider:
    def __init__(self, *, idempotent=False, fail_count=1):
        self.supports_idempotent_publish = idempotent
        self.fail_count = fail_count
        self.publish_calls = 0
        self.verify_calls = 0

    def publish_checkpoint(self, payload):
        self.publish_calls += 1
        if self.fail_count:
            self.fail_count -= 1
            raise TimeoutError("synthetic transient publish timeout")
        return "synthetic-reference"

    def verify_checkpoint(self, payload, external_reference):
        self.verify_calls += 1
        if self.verify_calls == 1:
            raise ConnectionError("synthetic transient read failure")
        return external_reference == "synthetic-reference"


class CheckpointRetryTests(unittest.TestCase):
    def test_publish_retries_only_when_service_declares_idempotency(self):
        unsafe = FlakyCheckpointProvider(idempotent=False)
        with self.assertRaises(TimeoutError):
            RetryingCheckpointProvider(unsafe, attempts=3, sleep=lambda _: None).publish_checkpoint(b"payload")
        self.assertEqual(unsafe.publish_calls, 1)

        safe = FlakyCheckpointProvider(idempotent=True)
        wrapper = RetryingCheckpointProvider(safe, attempts=3, sleep=lambda _: None)
        self.assertEqual(wrapper.publish_checkpoint(b"payload"), "synthetic-reference")
        self.assertEqual(safe.publish_calls, 2)

    def test_read_only_verification_retries_transient_failure_then_recovers(self):
        provider = FlakyCheckpointProvider(idempotent=False)
        wrapper = RetryingCheckpointProvider(provider, attempts=3, sleep=lambda _: None)
        self.assertTrue(wrapper.verify_checkpoint(b"payload", "synthetic-reference"))
        self.assertEqual(provider.verify_calls, 2)

    def test_retry_exhaustion_propagates_failure_without_false_success(self):
        class PermanentlyUnavailable(FlakyCheckpointProvider):
            def verify_checkpoint(self, payload, external_reference):
                self.verify_calls += 1
                raise ConnectionError("synthetic service unavailable")

        provider = PermanentlyUnavailable()
        wrapper = RetryingCheckpointProvider(provider, attempts=3, sleep=lambda _: None)
        with self.assertRaisesRegex(ConnectionError, "service unavailable"):
            wrapper.verify_checkpoint(b"payload", "synthetic-reference")
        self.assertEqual(provider.verify_calls, 3)

    def test_false_checkpoint_verification_is_not_retried_or_promoted(self):
        class CorruptCheckpoint(FlakyCheckpointProvider):
            def verify_checkpoint(self, payload, external_reference):
                self.verify_calls += 1
                return False

        provider = CorruptCheckpoint()
        result = RetryingCheckpointProvider(provider, attempts=3, sleep=lambda _: None).verify_checkpoint(
            b"payload", "corrupt-reference"
        )
        self.assertIs(result, False)
        self.assertEqual(provider.verify_calls, 1)

    def test_retry_configuration_is_bounded_and_validated(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            RetryingCheckpointProvider(FlakyCheckpointProvider(), attempts=0)


if __name__ == "__main__":
    unittest.main()
