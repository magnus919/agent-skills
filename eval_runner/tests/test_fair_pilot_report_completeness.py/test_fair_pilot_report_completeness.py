"""Keep the published fair-pilot report structurally complete."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "docs/fair-skill-evaluation-pilot.md"


def test_fair_pilot_report_keeps_ledger_backlog_and_release_limits():
    report = REPORT.read_text(encoding="utf-8")
    ledger_heading = "## Staged ledger"
    backlog_heading = "## Risk-ranked migration backlog"

    assert report.count(ledger_heading) == 1
    assert report.count(backlog_heading) == 1
    ledger = report.split(ledger_heading, 1)[1].split(backlog_heading, 1)[0]
    expected_workstreams = (
        "Truthful result semantics",
        "Case/evidence contracts and selector coverage",
        "Risk-representative pilot",
        "Deterministic mutation qualification",
        "Source-aware Jev qualification",
        "Fair comparison harness and proportional CI",
        "Repository evidence and test-route inventory",
        "Effectiveness confirmation",
    )
    assert all(f"| {workstream} |" in ledger for workstream in expected_workstreams)

    backlog = report.split(backlog_heading, 1)[1]
    priorities = [
        row.split("|", 2)[1].strip()
        for row in backlog.splitlines()
        if row.startswith(("| P0 |", "| P1 |", "| P2 |"))
    ]
    assert priorities == ["P0", "P0", "P1", "P1", "P2", "P2"]
    assert report.rstrip().endswith("This refit is not complete.")
