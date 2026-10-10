"""Independent contract outcomes for the non-chat proposal command boundary."""

from dataclasses import replace

import pytest

from eval_runner.fair_pilot_command_boundary import (
    Approval,
    ApprovedAction,
    Command,
    InMemoryCommandBoundary,
)


def _approved_command() -> tuple[InMemoryCommandBoundary, Command]:
    approval_action = ApprovedAction(
        operation="reserve",
        target_id="camera-1",
        parameters=(("destination", "warehouse-east"), ("quantity", "1")),
    )
    command_action = ApprovedAction(
        operation="reserve",
        target_id="camera-1",
        parameters=(("quantity", "1"), ("destination", "warehouse-east")),
    )
    approval = Approval(
        approval_id="approval-17",
        action=approval_action,
        record_revision="record-r17",
        policy_version="policy-v3",
    )
    command = Command(
        approval_id="approval-17",
        action=command_action,
        expected_record_revision="record-r17",
        policy_version="policy-v3",
        idempotency_key="command-8",
    )
    boundary = InMemoryCommandBoundary(
        current_permission=True,
        current_record_revision="record-r17",
        current_policy_version="policy-v3",
        approval=approval,
    )
    return boundary, command


@pytest.mark.parametrize(
    ("mutation", "expected_reason"),
    [
        ("permission_revoked", "permission_revoked"),
        ("current_record_revision", "current_record_revision_mismatch"),
        ("expected_record_revision", "approved_record_revision_mismatch"),
        ("current_policy_version", "current_policy_version_mismatch"),
        ("command_policy_version", "approved_policy_version_mismatch"),
        ("approval_id", "approval_mismatch"),
        ("action_operation", "approved_action_mismatch"),
        ("action_target", "approved_action_mismatch"),
        ("action_parameters", "approved_action_mismatch"),
    ],
)
def test_post_approval_mutations_return_to_review_without_writes(mutation, expected_reason):
    boundary, command = _approved_command()
    if mutation == "permission_revoked":
        boundary.current_permission = False
    elif mutation == "current_record_revision":
        boundary.current_record_revision = "record-r18"
    elif mutation == "expected_record_revision":
        command = replace(command, expected_record_revision="record-r18")
    elif mutation == "current_policy_version":
        boundary.current_policy_version = "policy-v4"
    elif mutation == "command_policy_version":
        command = replace(command, policy_version="policy-v4")
    elif mutation == "approval_id":
        command = replace(command, approval_id="approval-18")
    elif mutation == "action_operation":
        command = replace(command, action=replace(command.action, operation="cancel"))
    elif mutation == "action_target":
        command = replace(command, action=replace(command.action, target_id="camera-2"))
    elif mutation == "action_parameters":
        command = replace(
            command,
            action=replace(
                command.action,
                parameters=(("destination", "warehouse-east"), ("quantity", "2")),
            ),
        )

    result = boundary.execute(command)

    assert result.status == "review"
    assert result.reason == expected_reason
    assert boundary.state == "review"
    assert boundary.writes == []


def test_independently_constructed_equal_action_executes_expected_snapshot():
    boundary, command = _approved_command()

    assert boundary.approval.action is not command.action
    result = boundary.execute(command)

    assert result.status == "executed"
    assert boundary.state == "executed"
    assert len(boundary.writes) == 1
    write = boundary.writes[0]
    assert write.action is not boundary.approval.action
    assert write.action is not command.action
    assert write.action.operation == "reserve"
    assert write.action.target_id == "camera-1"
    assert write.action.parameters == (
        ("destination", "warehouse-east"),
        ("quantity", "1"),
    )


def test_approval_command_write_and_completion_use_independent_action_snapshots():
    caller_action = ApprovedAction(
        "reserve",
        "camera-1",
        (("destination", "warehouse-east"), ("quantity", "1")),
    )
    approval = Approval("approval-17", caller_action, "record-r17", "policy-v3")
    command_action = ApprovedAction(
        "reserve",
        "camera-1",
        (("destination", "warehouse-east"), ("quantity", "1")),
    )
    command = Command("approval-17", command_action, "record-r17", "policy-v3", "command-8")
    boundary = InMemoryCommandBoundary(True, "record-r17", "policy-v3", approval)

    result = boundary.execute(command)

    assert result.status == "executed"
    assert approval.action is not caller_action
    assert boundary.approval is not approval
    assert boundary.approval.action is not approval.action
    assert command.action is not command_action
    assert boundary.writes[0].action is not command.action
    assert boundary.writes[0].action is not boundary._completed_by_key["command-8"].action


def test_identical_new_command_replay_deduplicates_after_revocation():
    boundary, command = _approved_command()
    first = boundary.execute(command)
    boundary.current_permission = False
    equal_replay = Command(
        approval_id="approval-17",
        action=ApprovedAction(
            operation="reserve",
            target_id="camera-1",
            parameters=(("destination", "warehouse-east"), ("quantity", "1")),
        ),
        expected_record_revision="record-r17",
        policy_version="policy-v3",
        idempotency_key="command-8",
    )

    replay = boundary.execute(equal_replay)

    assert first.status == "executed"
    assert replay.status == "deduplicated"
    assert replay.reason == "already_executed"
    assert boundary.state == "executed"
    assert len(boundary.writes) == 1
    assert boundary.writes[0].action.parameters == (
        ("destination", "warehouse-east"),
        ("quantity", "1"),
    )


def test_conflicting_replay_is_reviewed_without_a_second_write():
    boundary, command = _approved_command()
    first = boundary.execute(command)
    conflicting = replace(command, action=replace(command.action, target_id="camera-2"))

    replay = boundary.execute(conflicting)

    assert first.status == "executed"
    assert replay.status == "review"
    assert replay.reason == "idempotency_key_conflict"
    assert boundary.state == "executed"
    assert len(boundary.writes) == 1


def test_rejected_approval_stays_in_review_even_if_old_values_are_restored():
    boundary, command = _approved_command()
    boundary.current_record_revision = "record-r18"

    stale_result = boundary.execute(command)
    boundary.current_record_revision = "record-r17"
    retry_result = boundary.execute(command)

    assert stale_result.status == "review"
    assert stale_result.reason == "current_record_revision_mismatch"
    assert retry_result.status == "review"
    assert retry_result.reason == "approval_not_current"
    assert boundary.state == "review"
    assert boundary.writes == []


@pytest.mark.parametrize("invalid_value", [1, True, None])
def test_non_string_parameter_values_are_rejected_before_action_comparison(invalid_value):
    boundary, _ = _approved_command()

    with pytest.raises(TypeError):
        ApprovedAction(
            operation="reserve",
            target_id="camera-1",
            parameters=(("quantity", invalid_value),),
        )

    assert boundary.state == "approved"
    assert boundary.writes == []


def test_mutable_nested_parameters_are_rejected_before_execution():
    boundary, command = _approved_command()
    mutable_parameters = [["destination", "warehouse-east"], ["quantity", "1"]]

    with pytest.raises(TypeError):
        ApprovedAction("reserve", "camera-1", mutable_parameters)

    mutable_parameters[1][1] = "99"
    result = boundary.execute(command)

    assert result.status == "executed"
    assert boundary.writes[0].action.parameters == (
        ("destination", "warehouse-east"),
        ("quantity", "1"),
    )


def test_approval_and_write_snapshots_cannot_be_mutated_after_execution():
    boundary, command = _approved_command()
    result = boundary.execute(command)
    write = boundary.writes[0]

    with pytest.raises(TypeError):
        write.action.parameters[0][1] = "99"
    with pytest.raises(TypeError):
        boundary.approval.action.parameters[0][1] = "99"

    assert result.status == "executed"
    assert write.action.parameters == (
        ("destination", "warehouse-east"),
        ("quantity", "1"),
    )
    assert boundary.approval.action.parameters == (
        ("destination", "warehouse-east"),
        ("quantity", "1"),
    )


@pytest.mark.parametrize("field_name", ["operation", "target_id"])
def test_action_identifiers_must_be_nonempty(field_name):
    values = {
        "operation": "reserve",
        "target_id": "camera-1",
        "parameters": (),
    }
    values[field_name] = ""

    with pytest.raises(ValueError):
        ApprovedAction(**values)


@pytest.mark.parametrize(
    ("approval_id", "record_revision", "policy_version"),
    [
        ("", "record-r17", "policy-v3"),
        ("approval-17", "", "policy-v3"),
        ("approval-17", "record-r17", ""),
    ],
)
def test_approval_ids_and_versions_must_be_nonempty(approval_id, record_revision, policy_version):
    action = ApprovedAction("reserve", "camera-1", ())

    with pytest.raises(ValueError):
        Approval(approval_id, action, record_revision, policy_version)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("approval_id", ""),
        ("expected_record_revision", ""),
        ("policy_version", ""),
        ("idempotency_key", ""),
    ],
)
def test_command_ids_and_versions_must_be_nonempty(field_name, invalid_value):
    _, command = _approved_command()

    with pytest.raises(ValueError):
        replace(command, **{field_name: invalid_value})


def test_malformed_command_and_current_state_fail_closed_before_equality():
    boundary, command = _approved_command()

    malformed_command = boundary.execute(None)
    assert malformed_command.status == "review"
    assert malformed_command.reason == "malformed_input"
    assert boundary.writes == []

    boundary, command = _approved_command()
    boundary.current_permission = 1
    malformed_state = boundary.execute(command)
    assert malformed_state.status == "review"
    assert malformed_state.reason == "malformed_input"
    assert boundary.writes == []


def test_boundary_rejects_invalid_permission_and_empty_current_versions():
    boundary, _ = _approved_command()

    with pytest.raises(TypeError):
        InMemoryCommandBoundary(1, "record-r17", "policy-v3", boundary.approval)
    with pytest.raises(ValueError):
        InMemoryCommandBoundary(True, "", "policy-v3", boundary.approval)
    with pytest.raises(ValueError):
        InMemoryCommandBoundary(True, "record-r17", "", boundary.approval)
