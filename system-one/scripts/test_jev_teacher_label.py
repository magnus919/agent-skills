"""Prediction-blind model-teacher packet and output contract tests."""

import json
import tempfile
import unittest
from pathlib import Path

from jev_teacher_label import (
    consensus,
    label_pass,
    local_endpoint,
    parse_labels,
    read_blind_items,
    request_payload,
    response_text,
)


class JevTeacherLabelTests(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"id": "j" + "1" * 20, "assertion": "Names a bounded retry deadline", "response": "No deadline is described."},
            {"id": "j" + "2" * 20, "assertion": "Specifies a fallback lane", "response": "No deadline is described."},
            {"id": "j" + "3" * 20, "assertion": "Shows authorization checking", "response": "Authorization is checked first."},
        ]

    def test_read_requires_blind_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "items.json"
            path.write_text(json.dumps({"schema_version": 1, "items": self.items}), encoding="utf-8")
            items, source_hash = read_blind_items(path)
            self.assertEqual(items, self.items)
            self.assertEqual(len(source_hash), 64)
            tainted = json.loads(path.read_text(encoding="utf-8"))
            tainted["items"][0]["suggested_verdict"] = "met"
            path.write_text(json.dumps(tainted), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "prediction-bearing"):
                read_blind_items(path)

    def test_request_has_no_jev_prediction_and_reverses_order(self):
        first = request_payload("openai/gpt-6-luna", self.items[0]["response"], self.items[:2], 1)
        second = request_payload("openai/gpt-6-luna", self.items[0]["response"], self.items[:2], 2)
        self.assertNotIn("suggested_verdict", json.dumps(first))
        self.assertNotIn("met_probability", json.dumps(first))
        self.assertEqual([a["id"] for a in json.loads(first["messages"][1]["content"])["assertions"]],
                         [self.items[0]["id"], self.items[1]["id"]])
        self.assertEqual([a["id"] for a in json.loads(second["messages"][1]["content"])["assertions"]],
                         [self.items[1]["id"], self.items[0]["id"]])
        self.assertFalse(first["stream"])
        self.assertNotIn("response_format", first)
        local = request_payload("local-model", self.items[0]["response"], self.items[:2], 1, structured=True)
        self.assertEqual(local["response_format"], {"type": "json_object"})

    def test_parsing_requires_exact_ids_and_evidence(self):
        entry = {"labels": [{"id": self.items[0]["id"], "label": "not_shown", "evidence": "No deadline supplied."}]}
        response = {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(entry)}}]}
        self.assertEqual(parse_labels(response, {self.items[0]["id"]})[self.items[0]["id"]]["label"], "not_shown")
        with self.assertRaisesRegex(ValueError, "omitted or added"):
            parse_labels(response, {self.items[0]["id"], self.items[1]["id"]})
        entry["labels"][0]["label"] = "pass"
        response["choices"][0]["message"]["content"] = json.dumps(entry)
        with self.assertRaisesRegex(ValueError, "invalid"):
            parse_labels(response, {self.items[0]["id"]})

    def test_remote_responses_request_and_strict_output(self):
        payload = request_payload("openai/gpt-6-luna", self.items[0]["response"], self.items[:2], 2,
                                  responses=True)
        self.assertEqual(payload["reasoning"], {"effort": "low"})
        self.assertFalse(payload["store"])
        self.assertNotIn("messages", payload)
        self.assertEqual([row["id"] for row in json.loads(payload["input"])["assertions"]],
                         [self.items[1]["id"], self.items[0]["id"]])
        self.assertNotIn("suggested_verdict", json.dumps(payload))
        answer = json.dumps({"labels": [{"id": self.items[0]["id"], "label": "not_shown",
                                        "evidence": "No deadline supplied."}]})
        result = {"status": "completed", "output": [{"type": "message", "role": "assistant",
                "content": [{"type": "output_text", "text": answer}]}]}
        self.assertEqual(parse_labels(result, {self.items[0]["id"]})[self.items[0]["id"]]["label"],
                         "not_shown")
        result["status"] = "incomplete"
        with self.assertRaisesRegex(ValueError, "incomplete"):
            response_text(result)
        result["status"] = "completed"
        result["output"].append(result["output"][0])
        with self.assertRaisesRegex(ValueError, "one final"):
            response_text(result)

    def test_bad_evidence_abstains_per_item_without_accepting_label(self):
        entries = [
            {"id": self.items[0]["id"], "label": "met", "evidence": ""},
            {"id": self.items[1]["id"], "label": "met", "evidence": "Evidence"},
        ]
        response = {"choices": [{"finish_reason": "stop", "message": {
            "content": json.dumps({"labels": entries})}}]}
        labels = parse_labels(response, {self.items[0]["id"], self.items[1]["id"]})
        self.assertEqual(labels[self.items[0]["id"]]["label"], "uncertain")
        self.assertEqual(labels[self.items[1]["id"]]["label"], "met")
        entries[0]["evidence"] = "x" * 501
        response["choices"][0]["message"]["content"] = json.dumps({"labels": entries})
        self.assertEqual(parse_labels(response, {self.items[0]["id"], self.items[1]["id"]})
                         [self.items[0]["id"]]["label"], "uncertain")

    def test_two_pass_consensus_abstains_on_disagreement(self):
        first = {item["id"]: {"label": "met", "evidence": "Visible support"} for item in self.items}
        second = {item["id"]: {"label": "met", "evidence": "Visible support"} for item in self.items}
        second[self.items[1]["id"]]["label"] = "not_shown"
        full, summary = consensus(self.items, first, second, "openai/gpt-6-luna", "0" * 64)
        self.assertEqual([item["label"] for item in full["labels"]], ["met", "uncertain", "met"])
        self.assertEqual(summary["agreement_non_uncertain"], 2)
        self.assertNotIn("Visible support", json.dumps(summary))
        self.assertNotIn("No deadline is described", json.dumps(summary))
        self.assertEqual(summary["label_source"], "model_teacher_pseudo_labels")

    def test_fake_transport_groups_shared_response(self):
        seen = []

        def fake_transport(payload):
            question = json.loads(payload["messages"][1]["content"])
            seen.append(question)
            answer = {"labels": [{"id": item["id"], "label": "not_shown", "evidence": "Required detail missing"}
                                 for item in question["assertions"]]}
            return {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps(answer)}}]}

        labels = label_pass(self.items, "openai/gpt-6-luna", 1, fake_transport)
        self.assertEqual(len(seen), 2)
        self.assertEqual(len(labels), 3)
        self.assertEqual({row["label"] for row in labels.values()}, {"not_shown"})

    def test_local_endpoint_is_restricted_to_existing_runner_service(self):
        self.assertEqual(local_endpoint("http://host.docker.internal:8080"),
                         "http://host.docker.internal:8080/v1/chat/completions")
        for bad in ("https://host.docker.internal:8080", "http://example.com:8080",
                    "http://host.docker.internal:8080/path", "http://host.docker.internal:8080/?x=1"):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "local model base URL"):
                local_endpoint(bad)

    def test_public_local_summary_redacts_model_id(self):
        labels = {item["id"]: {"label": "met", "evidence": "Visible support"} for item in self.items}
        full, summary = consensus(self.items, labels, labels, "private-model", "0" * 64,
                                  ["private-model"], "configured-local-model")
        self.assertIn("private-model", json.dumps(full))
        self.assertNotIn("private-model", json.dumps(summary))
        self.assertEqual(summary["model_requested"], "configured-local-model")
        self.assertEqual(len(summary["provider_reported_model_hashes"][0]), 64)


if __name__ == "__main__":
    unittest.main()
