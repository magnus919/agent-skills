#!/usr/bin/env python3
"""Compute the five current DORA metrics from a deployment events file.

Input: --events <file.json> with the schema:
  {
    "deployments": [
      {"started_at": "<iso>", "finished_at": "<iso>", "commit_sha": "<sha>",
       "environment": "prod", "success": true, "unplanned": false}
    ],
    "commits": [{"sha": "<sha>", "created_at": "<iso>"}]
  }

Metrics (scoped to --environment, default "prod"):

  1. Deployment frequency        Successful deployments per day. The
                                 observation window spans the earliest
                                 deployment start to the latest deployment
                                 finish among deployments in the selected
                                 environment (minimum 1 day), so mixed-
                                 environment events files do not widen the
                                 window with other environments' activity.
                                 If the environment has zero deployments,
                                 the window is unavailable and the metric
                                 is reported as unavailable.
  2. Change lead time            Median of (finished_at - commit created_at)
                                 over successful deployments whose commit_sha
                                 resolves to a commit with a timestamp. A
                                 negative duration (a deployment finishing
                                 before its commit was created) is clamped
                                 to 0. Reported as unavailable when no
                                 deployment has commit timestamp data.
  3. Change failure rate         (failed / total) * 100.
  4. Failed deployment recovery time
                                 Median of (next successful deployment
                                 finished_at - failed deployment started_at)
                                 over failed deployments that have a later
                                 successful deployment. A recovery
                                 deployment counts only if it starts at or
                                 after the failed deployment finished (a
                                 success that began mid-failure is not a
                                 recovery). Reported as unavailable when a
                                 failed deployment has not yet been
                                 recovered (or there are none).
  5. Deployment rework rate      (unplanned / total) * 100.

Timestamps are ISO-8601 strings ('Z' suffix accepted; naive timestamps are
treated as UTC). Metrics whose computation is not meaningful for the data
are reported with "available": false and a reason, and the script still
exits 0 for well-formed input.

Output is a human-readable table by default, or structured JSON with --json.

Exit codes:
  0  success (metrics computed or reported unavailable)
  1  input error (unreadable file, invalid JSON, malformed events)
  2  usage error (argparse)
"""

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone

SECONDS_PER_DAY = 86400.0


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="dora_metrics.py",
        description=(
            "Compute the five current DORA metrics (deployment frequency, "
            "change lead time, change failure rate, failed deployment "
            "recovery time, deployment rework rate) from an events JSON file."
        ),
        epilog=(
            "Exit codes: 0 success, 1 input error, 2 usage error.\n\n"
            "Examples:\n"
            "  dora_metrics.py --events events.json\n"
            "  dora_metrics.py --events events.json --environment staging\n"
            "  dora_metrics.py --events events.json --json\n"
        ),
    )
    parser.add_argument(
        "--events",
        metavar="FILE",
        required=True,
        help="Path to the deployment events JSON file.",
    )
    parser.add_argument(
        "--environment",
        metavar="NAME",
        default="prod",
        help="Environment to scope metrics to (default: prod).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as machine-parseable JSON instead of a table.",
    )
    return parser.parse_args(argv)


def parse_iso(value):
    """Parse an ISO-8601 timestamp; returns datetime or None."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_events(path):
    """Load and validate the events file.

    Returns (events, None) on success or (None, error_message).
    events = {"deployments": [...], "commits": {sha: created_at_datetime}}
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        return None, "cannot read events file: {}".format(exc)
    except ValueError as exc:
        return None, "invalid JSON in events file: {}".format(exc)

    if not isinstance(data, dict):
        return None, "events must be a JSON object with 'deployments' and 'commits'"
    deployments = data.get("deployments", [])
    commits = data.get("commits", [])
    if not isinstance(deployments, list):
        return None, "'deployments' must be an array"
    if not isinstance(commits, list):
        return None, "'commits' must be an array"

    normalized = []
    for index, deploy in enumerate(deployments):
        if not isinstance(deploy, dict):
            return None, "deployment {} is not an object".format(index)
        started = parse_iso(deploy.get("started_at"))
        if started is None:
            return None, "deployment {} has an invalid 'started_at'".format(index)
        finished = parse_iso(deploy.get("finished_at"))
        if finished is None:
            return None, "deployment {} has an invalid 'finished_at'".format(index)
        environment = deploy.get("environment")
        if not isinstance(environment, str) or not environment.strip():
            return None, "deployment {} has an invalid 'environment'".format(index)
        success = deploy.get("success")
        if not isinstance(success, bool):
            return None, "deployment {} field 'success' must be a boolean".format(index)
        unplanned = deploy.get("unplanned")
        if not isinstance(unplanned, bool):
            return None, "deployment {} field 'unplanned' must be a boolean".format(index)
        commit_sha = deploy.get("commit_sha")
        if commit_sha is not None and not isinstance(commit_sha, str):
            return None, "deployment {} field 'commit_sha' must be a string".format(index)
        normalized.append(
            {
                "started_at": started,
                "finished_at": finished,
                "environment": environment,
                "success": success,
                "unplanned": unplanned,
                "commit_sha": commit_sha,
            }
        )

    commit_map = {}
    for index, commit in enumerate(commits):
        if not isinstance(commit, dict):
            return None, "commit {} is not an object".format(index)
        sha = commit.get("sha")
        if not isinstance(sha, str) or not sha.strip():
            return None, "commit {} has an invalid 'sha'".format(index)
        created = parse_iso(commit.get("created_at"))
        if created is None:
            # Commit without a usable timestamp: contributes no lead-time
            # data (reported as unavailable rather than failing the file).
            continue
        commit_map[sha] = created

    return {"deployments": normalized, "commits": commit_map}, None


def observation_window(deployments):
    """Return (window_days, min_start, max_finish) over the given deployments.

    The window spans the earliest started_at to the latest finished_at;
    it is clamped to a minimum of one day so frequency is well-defined
    for single-deployment windows. Pass the environment-filtered
    deployment set so mixed-environment events files do not widen the
    window with other environments' activity.
    """
    if not deployments:
        return 1.0, None, None
    min_start = min(d["started_at"] for d in deployments)
    max_finish = max(d["finished_at"] for d in deployments)
    span = (max_finish - min_start).total_seconds()
    window_days = max(1.0, span / SECONDS_PER_DAY)
    return window_days, min_start, max_finish


def compute_metrics(events, environment):
    """Compute the five DORA metrics for an environment.

    Returns a dict of metric payloads (each with an 'available' flag).
    """
    deployments = [d for d in events["deployments"] if d["environment"] == environment]
    total = len(deployments)
    successful = [d for d in deployments if d["success"]]
    failed = [d for d in deployments if not d["success"]]
    unplanned = [d for d in deployments if d["unplanned"]]

    no_deploys_reason = "no deployments in environment '{}'".format(environment)

    # 1. Deployment frequency: successful prod deploys per day, over a
    # window scoped to this environment's deployments.
    window_days, _, _ = observation_window(deployments)
    if total == 0:
        deployment_frequency = {"available": False, "reason": no_deploys_reason}
    else:
        deployment_frequency = {
            "available": True,
            "deployments_per_day": _round(len(successful) / window_days),
            "successful_deployments": len(successful),
            "window_days": _round(window_days),
        }

    # 2. Change lead time: median finished_at - commit created_at.
    lead_times = []
    without_commit_data = 0
    for deploy in successful:
        sha = deploy.get("commit_sha")
        created = events["commits"].get(sha) if sha else None
        if created is None:
            without_commit_data += 1
            continue
        # Clamp negative durations (a deployment finishing before its
        # commit was created) to zero rather than reporting negative time.
        lead_times.append(
            max(0.0, (deploy["finished_at"] - created).total_seconds())
        )
    if not lead_times:
        change_lead_time = {
            "available": False,
            "reason": (
                "no successful deployments with commit timestamp data "
                "in environment '{}'".format(environment)
            ),
            "deployments_measured": 0,
            "deployments_without_commit_data": without_commit_data,
        }
    else:
        change_lead_time = {
            "available": True,
            "seconds": _round(statistics.median(lead_times)),
            "human": format_duration(statistics.median(lead_times)),
            "deployments_measured": len(lead_times),
            "deployments_without_commit_data": without_commit_data,
        }

    # 3. Change failure rate: failed / total as a percentage.
    if total == 0:
        change_failure_rate = {"available": False, "reason": no_deploys_reason}
    else:
        change_failure_rate = {
            "available": True,
            "percent": _round(len(failed) / total * 100.0),
            "failed": len(failed),
            "total": total,
        }

    # 4. Failed deployment recovery time: median next-success - failed start.
    # A recovery deployment must start at or after the failed deployment
    # finished, so a success that began mid-failure is not counted.
    ordered = sorted(deployments, key=lambda d: (d["started_at"], d["finished_at"]))
    recoveries = []
    unrecovered = 0
    for index, deploy in enumerate(ordered):
        if deploy["success"]:
            continue
        next_success = None
        for candidate in ordered[index + 1:]:
            if candidate["success"] and candidate["started_at"] >= deploy["finished_at"]:
                next_success = candidate
                break
        if next_success is None:
            unrecovered += 1
        else:
            recoveries.append((next_success["finished_at"] - deploy["started_at"]).total_seconds())
    if len(failed) == 0:
        failed_deployment_recovery_time = {
            "available": False,
            "reason": "no failed deployments to recover from",
            "recovered": 0,
            "unrecovered": 0,
        }
    elif unrecovered > 0:
        failed_deployment_recovery_time = {
            "available": False,
            "reason": "{} failed deployment(s) not yet recovered".format(unrecovered),
            "recovered": len(recoveries),
            "unrecovered": unrecovered,
        }
    else:
        failed_deployment_recovery_time = {
            "available": True,
            "seconds": _round(statistics.median(recoveries)),
            "human": format_duration(statistics.median(recoveries)),
            "recovered": len(recoveries),
            "unrecovered": 0,
        }

    # 5. Deployment rework rate: unplanned / total as a percentage.
    if total == 0:
        deployment_rework_rate = {"available": False, "reason": no_deploys_reason}
    else:
        deployment_rework_rate = {
            "available": True,
            "percent": _round(len(unplanned) / total * 100.0),
            "unplanned": len(unplanned),
            "total": total,
        }

    return {
        "environment": environment,
        "window_days": _round(window_days),
        "deployments": {
            "total": total,
            "successful": len(successful),
            "failed": len(failed),
            "unplanned": len(unplanned),
        },
        "deployment_frequency": deployment_frequency,
        "change_lead_time": change_lead_time,
        "change_failure_rate": change_failure_rate,
        "failed_deployment_recovery_time": failed_deployment_recovery_time,
        "deployment_rework_rate": deployment_rework_rate,
    }


def _round(value):
    """Round a float to 6 decimal places for deterministic output."""
    return round(value, 6)


def format_duration(seconds):
    """Format a duration in seconds as a compact human string."""
    total = int(round(seconds))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append("{}d".format(days))
    if hours:
        parts.append("{}h".format(hours))
    if minutes:
        parts.append("{}m".format(minutes))
    if secs or not parts:
        parts.append("{}s".format(secs))
    return " ".join(parts)


def format_table(metrics):
    """Format metrics as a human-readable table."""
    counts = metrics["deployments"]
    lines = []
    lines.append("DORA metrics (environment: {})".format(metrics["environment"]))
    lines.append("-" * 72)
    df = metrics["deployment_frequency"]
    if df["available"]:
        lines.append(
            "{:<34} {} per day ({} successful over {} days)".format(
                "deployment frequency",
                df["deployments_per_day"],
                df["successful_deployments"],
                df["window_days"],
            )
        )
    else:
        lines.append(
            "{:<34} unavailable ({})".format("deployment frequency", df["reason"])
        )
    clt = metrics["change_lead_time"]
    if clt["available"]:
        lines.append(
            "{:<34} {} (median over {} deployment{})".format(
                "change lead time",
                clt["human"],
                clt["deployments_measured"],
                "" if clt["deployments_measured"] == 1 else "s",
            )
        )
    else:
        lines.append(
            "{:<34} unavailable ({})".format("change lead time", clt["reason"])
        )
    cfr = metrics["change_failure_rate"]
    if cfr["available"]:
        lines.append(
            "{:<34} {}% ({} of {})".format(
                "change failure rate", cfr["percent"], cfr["failed"], cfr["total"]
            )
        )
    else:
        lines.append(
            "{:<34} unavailable ({})".format("change failure rate", cfr["reason"])
        )
    fdrt = metrics["failed_deployment_recovery_time"]
    if fdrt["available"]:
        lines.append(
            "{:<34} {} (median over {} recovery{})".format(
                "failed deployment recovery time",
                fdrt["human"],
                fdrt["recovered"],
                "" if fdrt["recovered"] == 1 else "ies",
            )
        )
    else:
        lines.append(
            "{:<34} unavailable ({})".format(
                "failed deployment recovery time", fdrt["reason"]
            )
        )
    drr = metrics["deployment_rework_rate"]
    if drr["available"]:
        lines.append(
            "{:<34} {}% ({} of {})".format(
                "deployment rework rate", drr["percent"], drr["unplanned"], drr["total"]
            )
        )
    else:
        lines.append(
            "{:<34} unavailable ({})".format("deployment rework rate", drr["reason"])
        )
    lines.append("-" * 72)
    lines.append(
        "deployments in environment: {} total, {} successful, {} failed, {} unplanned".format(
            counts["total"],
            counts["successful"],
            counts["failed"],
            counts["unplanned"],
        )
    )
    return "\n".join(lines)


def main(argv=None):
    """Entry point."""
    args = parse_args(argv)
    events, err = load_events(args.events)
    if err:
        print("error: {}".format(err), file=sys.stderr)
        return 1

    metrics = compute_metrics(events, args.environment)

    if args.json_output:
        print(json.dumps(metrics, indent=2))
    else:
        print(format_table(metrics))

    return 0


if __name__ == "__main__":
    sys.exit(main())
