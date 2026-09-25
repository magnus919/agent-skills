import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("decision_battery", ROOT / "scripts/decision_battery.py")
battery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(battery)


class DecisionBatteryTests(unittest.TestCase):
    def test_v2_corpus_coverage_and_gold_contract(self):
        cases = battery.read_cases(ROOT / "examples/decision-battery-v2.jsonl")
        self.assertEqual(len(cases), 1800)
        self.assertEqual(len({case["scenario"] for case in cases}), 600)
        self.assertEqual(len({case["domain"] for case in cases}), 12)
        self.assertEqual({p: sum(case["primitive"] == p for case in cases)
                          for p in ("choice", "noul", "score")},
                         {"choice": 600, "noul": 600, "score": 600})
        for domain in {case["domain"] for case in cases}:
            self.assertEqual(sum(case["domain"] == domain for case in cases), 150)
            self.assertEqual({case["difficulty"] for case in cases if case["domain"] == domain},
                             {"easy", "medium", "hard"})
        for scenario in {case["scenario"] for case in cases}:
            group = [case for case in cases if case["scenario"] == scenario]
            self.assertEqual(len(group), 3)
            self.assertEqual(len({case["text"] for case in group}), 1)

    def test_v2_typed_noul_and_score_projection(self):
        cases = [
            {"schema_version": 2, "scenario": "n", "id": "n", "task": "noul", "primitive": "noul",
             "question": "Is it urgent?", "text": "yes", "choices": ["yes", "no"], "expected": "yes"},
            {"schema_version": 2, "scenario": "s", "id": "s", "task": "score", "primitive": "score",
             "question": "How many fields?", "text": "two", "choices": ["0", "1", "2", "3"], "expected": "2"},
        ]
        replies = [
            {"answers": {"noul": {"type": "noul", "noul": 0.7}}},
            {"answers": {"score": {"type": "score", "score": 1.8,
              "confidence": 0.8, "probabilities": {"0": 0, "1": 0.2, "2": 0.8, "3": 0},
              "legend": {"0": "0", "1": "1", "2": "2", "3": "3"}}}},
        ]
        sent = []

        class Response:
            def __init__(self, value): self.value = value
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self): return json.dumps(self.value).encode()

        def fake_urlopen(request, timeout):
            sent.append(json.loads(request.data))
            return Response(replies.pop(0))

        with patch.object(battery.urllib.request, "urlopen", fake_urlopen):
            result = battery.query_endpoint(cases, "https://example.test/v1/systemone", 1,
                                            adapter="systemone")
        self.assertEqual([sent[0]["questions"]["noul"]["type"],
                          sent[1]["questions"]["score"]["type"]], ["noul", "score"])
        self.assertNotIn("expected", json.dumps(sent))
        self.assertEqual(result["n"]["answer"], "yes")
        self.assertEqual(result["n"]["noul"], 0.7)
        self.assertEqual(result["s"]["answer"], "2")
        self.assertEqual(result["s"]["score"], 1.8)

    def test_v2_batches_three_questions_without_gold(self):
        cases = [
            {"schema_version": 2, "scenario": "one", "domain": "software",
             "difficulty": "easy", "slice": "direct", "id": f"one-{task}",
             "task": task, "primitive": task, "question": f"Question for {task}?",
             "text": "same live record", "choices": choices, "expected": expected}
            for task, choices, expected in (
                ("choice", ["a", "b"], "a"),
                ("noul", ["yes", "no"], "yes"),
                ("score", ["0", "1", "2", "3"], "2"),
            )
        ]
        sent = []

        class Response:
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self):
                return b'{"result":{"choice":"a","noul":"yes","score":"2"}}'

        def fake_urlopen(request, timeout):
            sent.append(json.loads(request.data))
            return Response()

        with patch.object(battery.urllib.request, "urlopen", fake_urlopen):
            result = battery.query_endpoint(cases, "http://example.test", 1)
        self.assertEqual(len(sent), 1)
        self.assertEqual(set(sent[0]["heads"]), {"choice", "noul", "score"})
        self.assertNotIn("expected", json.dumps(sent))
        self.assertEqual({key: value["answer"] for key, value in result.items()},
                         {"one-choice": "a", "one-noul": "yes", "one-score": "2"})
        self.assertEqual(battery.score(cases, result)["client_latency_ms"]["n"], 1)
        self.assertEqual({value["request_group_size"] for value in result.values()}, {3})

    def test_fixture_has_balanced_tasks_and_unique_ids(self):
        cases = battery.read_cases(ROOT / "examples/decision-battery-v1.jsonl")
        self.assertEqual(len(cases), 48)
        self.assertEqual({task: sum(c["task"] == task for c in cases) for task in
                          {c["task"] for c in cases}}, {
            "handoff": 8, "intent": 8, "queue": 8,
            "urgency": 8, "finished": 8, "policy": 8,
        })

    def test_score_counts_missing_invalid_and_false_negative(self):
        cases = [
            {"id": "a", "task": "handoff", "slice": "explicit",
             "text": "person", "choices": ["yes", "no"], "expected": "yes"},
            {"id": "b", "task": "handoff", "slice": "ordinary",
             "text": "status", "choices": ["yes", "no"], "expected": "no"},
            {"id": "c", "task": "intent", "slice": "refund",
             "text": "refund", "choices": ["refund", "other"], "expected": "refund"},
        ]
        result = battery.score(cases, {
            "a": {"id": "a", "answer": "no"},
            "b": {"id": "b", "answer": "no"},
            "c": {"id": "c", "answer": "not_a_choice"},
        })
        self.assertEqual(result["correct"], 1)
        self.assertEqual(result["handoff_false_negatives"], 1)
        self.assertEqual(len(result["errors"]), 2)

    def test_rejects_duplicate_fixture_id(self):
        case = {"id": "same", "task": "intent", "slice": "test", "text": "x",
                "choices": ["a", "b"], "expected": "a"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.jsonl"
            path.write_text(json.dumps(case) + "\n" + json.dumps(case) + "\n")
            with self.assertRaisesRegex(ValueError, "duplicate id"):
                battery.read_cases(path)

    def test_live_request_does_not_send_expected_label(self):
        case = {"id": "x", "task": "handoff", "slice": "explicit",
                "text": "Get me a person", "choices": ["yes", "no"], "expected": "yes"}

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return b'{"result":{"handoff":"yes"}}'

        sent = []

        def fake_urlopen(request, timeout):
            sent.append(json.loads(request.data))
            return Response()

        with patch.object(battery.urllib.request, "urlopen", fake_urlopen):
            result = battery.query_endpoint([case], "http://localhost:8091", 1)
        self.assertEqual(result["x"]["answer"], "yes")
        self.assertEqual(sent, [{"text": "Get me a person", "heads": {"handoff": ["yes", "no"]}}])

    def test_systemone_adapter_uses_typed_choice_and_validates_response(self):
        case = {"id": "x", "task": "handoff", "slice": "explicit",
                "text": "Get me a person", "choices": ["yes", "no"], "expected": "yes"}
        valid_response = {
            "model": "laya-rl-agent",
            "answers": {"handoff": {
                "type": "choice", "choice": "yes", "confidence": 0.8,
                "probabilities": {"yes": 0.8, "no": 0.2},
            }},
        }
        sent = []

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return json.dumps(valid_response).encode()

        def fake_urlopen(request, timeout):
            sent.append((json.loads(request.data), request.get_header("Authorization")))
            return Response()

        with patch.object(battery.urllib.request, "urlopen", fake_urlopen):
            result = battery.query_endpoint(
                [case], "https://example.test/v1/systemone", 1,
                adapter="systemone", api_key="test-token", model="jev-latest",
            )
        self.assertEqual(result["x"]["answer"], "yes")
        payload, auth = sent[0]
        self.assertEqual(auth, "Bearer test-token")
        self.assertEqual(payload["state"], {"text": case["text"]})
        self.assertEqual(payload["model"], "jev-latest")
        self.assertEqual(payload["questions"]["handoff"]["criteria"], {"yes": "yes", "no": "no"})
        self.assertEqual(payload["questions"]["handoff"]["type"], "choice")
        self.assertNotIn("expected", str(payload))

        valid_response["answers"]["handoff"]["probabilities"] = {"yes": 0.8, "no": 0.8}
        with patch.object(battery.urllib.request, "urlopen", fake_urlopen):
            invalid = battery.query_endpoint(
                [case], "https://example.test/v1/systemone", 1, adapter="systemone",
            )
        self.assertEqual(invalid["x"]["error"], "ValueError")

    def test_paired_comparison_preserves_case_level_disagreements(self):
        cases = [
            {"id": "a", "task": "handoff", "slice": "explicit", "text": "person",
             "choices": ["yes", "no"], "expected": "yes"},
            {"id": "b", "task": "handoff", "slice": "ordinary", "text": "status",
             "choices": ["yes", "no"], "expected": "no"},
        ]
        paired = battery.compare(
            cases,
            {"a": {"answer": "yes"}, "b": {"answer": "yes"}},
            {"a": {"answer": "no"}, "b": {"answer": "no"}},
        )
        self.assertEqual(paired["primary_only"], 1)
        self.assertEqual(paired["comparison_only"], 1)
        self.assertEqual(paired["agreement"], 0)
        self.assertEqual([item["id"] for item in paired["disagreements"]], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
