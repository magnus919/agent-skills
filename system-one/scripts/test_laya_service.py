#!/usr/bin/env python3
"""Offline tests for the private-service policy; no weights or network needed."""

import unittest

from laya_service import DecisionService


class FakeAgent:
    device = "cpu"

    def predict(self, state, questions):
        return {"model": "fake", "answers": {"route": {
            "type": "choice", "choice": "other",
            "probabilities": {"billing": 0.2, "other": 0.8}, "confidence": 0.8,
        }}}


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = DecisionService(FakeAgent(), "/model", "cpu")
        self.request = {"state": {"text": "hello"}, "questions": {"route": {
            "type": "choice", "instructions": "Which route?",
            "criteria": {"billing": "payment", "other": "unknown"},
        }}}

    def test_valid_inference(self):
        self.assertEqual(self.service.decide(self.request)["answers"]["route"]["choice"], "other")
        self.assertEqual(self.service.requests, 1)

    def test_wrong_device_not_ready(self):
        self.service.expected_device = "cuda"
        with self.assertRaisesRegex(RuntimeError, "expected device"):
            self.service.decide(self.request)

    def test_busy_worker_rejects(self):
        self.service.lock.acquire()
        try:
            with self.assertRaises(BlockingIOError):
                self.service.decide(self.request)
        finally:
            self.service.lock.release()

    def test_option_limit(self):
        self.request["questions"]["route"]["criteria"] = {str(i): str(i) for i in range(65)}
        with self.assertRaisesRegex(ValueError, "too many options"):
            self.service.decide(self.request)


if __name__ == "__main__":
    unittest.main()
