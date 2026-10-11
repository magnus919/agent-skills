"""Finite source-code mutation sensitivity checks for the command boundary."""

import eval_runner.fair_pilot_command_boundary_mutations as mutation_runner
from eval_runner.fair_pilot_command_boundary_mutations import (
    EXPECTED_IMPLEMENTATION_SHA256,
    EXPECTED_TESTS_SHA256,
    run_mutation_suite,
)


def test_five_source_gate_mutants_are_killed_and_equivalent_control_passes():
    report = run_mutation_suite()

    assert report["status"] == "pass"
    assert report["evidence_classification"] == "finite mutation sensitivity only"
    assert report["source"]["sha256"] == EXPECTED_IMPLEMENTATION_SHA256
    assert report["regression_tests"]["sha256"] == EXPECTED_TESTS_SHA256
    assert report["baseline"]["kind"] == "passed"
    assert [row["id"] for row in report["source_mutants"]["killed"]] == [
        "bypass-current-permission-gate",
        "bypass-record-revision-gates",
        "bypass-policy-version-gates",
        "bypass-exact-approved-action-gate",
        "bypass-identical-replay-response-deduplication",
    ]
    assert report["source_mutants"]["survived"] == []
    assert [row["id"] for row in report["equivalent_control"]["passed"]] == [
        "permission-bool-equivalent-spelling"
    ]
    assert report["equivalent_control"]["changed_behavior"] == []
    assert report["invalid_mutants"] == []
    assert report["infrastructure_errors"] == []


def test_campaign_uses_captured_test_bytes_after_backing_file_changes(tmp_path, monkeypatch):
    backing_file = tmp_path / "test_fair_pilot_command_boundary.py"
    captured_tests = mutation_runner.REGRESSION_TESTS.read_bytes()
    backing_file.write_bytes(captured_tests)
    monkeypatch.setattr(mutation_runner, "REGRESSION_TESTS", backing_file)

    original_run_tests = mutation_runner._run_tests
    changed_backing_file = False

    def change_backing_file_before_overlay(mutated_source, test_nodes, regression_test_bytes):
        nonlocal changed_backing_file
        if not changed_backing_file:
            backing_file.write_text(
                "raise RuntimeError('changed backing regression file was executed')\n",
                encoding="utf-8",
            )
            changed_backing_file = True
        return original_run_tests(mutated_source, test_nodes, regression_test_bytes)

    monkeypatch.setattr(mutation_runner, "_run_tests", change_backing_file_before_overlay)
    report = run_mutation_suite()

    assert changed_backing_file
    assert report["status"] == "pass"
    assert report["regression_tests"]["sha256"] == EXPECTED_TESTS_SHA256
    assert report["baseline"]["summary"][0].startswith("30 passed")
    assert len(report["source_mutants"]["killed"]) == 5
    assert report["equivalent_control"]["passed"]
    assert backing_file.read_text(encoding="utf-8").startswith("raise RuntimeError")
