"""Offline regression cases; these do not certify tokenizer/GPU compatibility."""

import copy
import unittest

from sft_audit import audit_batch, distribution, prepare_row, score


class Tokenizer:
    def apply_chat_template(self, messages, add_generation_prompt, **kwargs):
        prompt = [1, 2, 3]
        return prompt if add_generation_prompt else [*prompt, 4, 5, 6]

    def decode(self, ids, **kwargs):
        return "answer<eos>"


class Audits(unittest.TestCase):
    def setUp(self):
        self.row = {
            "messages": [
                {"role": "user", "content": "prompt"},
                {"role": "assistant", "content": "answer"},
            ]
        }
        self.feature, self.record = prepare_row(Tokenizer(), self.row, 10)
        self.batch = {
            k: [v + ([-100] * 2 if k == "labels" else [0] * 2)] for k, v in self.feature.items()
        }

    def test_correct_labels_and_padding(self):
        self.assertEqual(audit_batch([self.feature], self.batch), [3])
        self.assertEqual(self.record["supervised_tokens"], 3)
        self.assertEqual(self.feature["labels"], [-100, -100, -100, 4, 5, 6])

    def test_partial_and_total_answer_truncation(self):
        for length in (2, 3, 5):
            with self.assertRaisesRegex(ValueError, "truncated"):
                prepare_row(Tokenizer(), self.row, length)

    def test_template_prefix_mismatch(self):
        class Wrong(Tokenizer):
            def apply_chat_template(self, messages, add_generation_prompt, **kwargs):
                return [9] if add_generation_prompt else [1, 2, 3, 4]

        with self.assertRaisesRegex(ValueError, "prefix"):
            prepare_row(Wrong(), self.row, 10)

    def test_collator_supervises_prompt(self):
        bad = copy.deepcopy(self.batch)
        bad["labels"][0][0] = 1
        with self.assertRaisesRegex(ValueError, "label mask"):
            audit_batch([self.feature], bad)

    def test_padding_is_supervised(self):
        bad = copy.deepcopy(self.batch)
        bad["labels"][0][-1] = 0
        with self.assertRaisesRegex(ValueError, "padding"):
            audit_batch([self.feature], bad)

    def test_padding_is_attended(self):
        bad = copy.deepcopy(self.batch)
        bad["attention_mask"][0][-1] = 1
        with self.assertRaisesRegex(ValueError, "padding"):
            audit_batch([self.feature], bad)

    def test_collator_drops_row(self):
        bad = {k: [] for k in self.batch}
        with self.assertRaisesRegex(ValueError, "batch size"):
            audit_batch([self.feature], bad)

    def test_lengths_and_scoring(self):
        self.assertEqual(distribution([1, 2, 3, 100])["95"], 100)
        self.assertEqual(score(" RED\n", "RED"), 1)
        self.assertEqual(score("The color is RED", "RED"), 0)

    def test_reject_multi_turn(self):
        bad = copy.deepcopy(self.row)
        bad["messages"].append({"role": "user", "content": "next"})
        with self.assertRaisesRegex(ValueError, "exactly"):
            prepare_row(Tokenizer(), bad, 10)


class BatchShapes(unittest.TestCase):
    def test_missing_labels_row_is_not_silently_zipped(self):
        feature = {"input_ids": [1], "attention_mask": [1], "labels": [1]}
        with self.assertRaisesRegex(ValueError, "batch size"):
            audit_batch([feature], {"input_ids": [[1]], "labels": [], "attention_mask": [[1]]})

    def test_width_mismatch(self):
        feature = {"input_ids": [1], "attention_mask": [1], "labels": [1]}
        with self.assertRaisesRegex(ValueError, "widths"):
            audit_batch(
                [feature], {"input_ids": [[1]], "labels": [[1]], "attention_mask": [[1, 0]]}
            )


if __name__ == "__main__":
    unittest.main()
