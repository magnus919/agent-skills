"""In-memory reference mechanics for the fair pilot's command boundary.

The supplied Approval is a trusted application-owned fixture. This harness
does not authenticate an approver or connect to a production command path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


def _require_token(value: object, field_name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{field_name} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{field_name} must be non-empty and trimmed")
    return value


def _canonical_parameters(parameters: object) -> tuple[tuple[str, str], ...]:
    if type(parameters) is not tuple:
        raise TypeError("parameters must be an immutable tuple")

    pairs: list[tuple[str, str]] = []
    seen_keys: set[str] = set()
    for index, pair in enumerate(parameters):
        if type(pair) is not tuple or len(pair) != 2:
            raise TypeError(f"parameters[{index}] must be a two-item tuple")
        key = _require_token(pair[0], f"parameters[{index}].key")
        value = pair[1]
        if type(value) is not str:
            raise TypeError(f"parameters[{index}].value must be a string")
        if key in seen_keys:
            raise ValueError(f"duplicate parameter key: {key}")
        seen_keys.add(key)
        pairs.append((key, value))

    return tuple(sorted(pairs, key=lambda item: item[0]))


def _validated_action(action: object) -> ApprovedAction:
    if type(action) is not ApprovedAction:
        raise TypeError("action must be an ApprovedAction")
    _require_token(action.operation, "action.operation")
    _require_token(action.target_id, "action.target_id")
    canonical = _canonical_parameters(action.parameters)
    if canonical != action.parameters:
        raise ValueError("action.parameters must be canonical")
    return action


def _validated_approval(approval: object) -> Approval:
    if type(approval) is not Approval:
        raise TypeError("approval must be an Approval")
    _require_token(approval.approval_id, "approval.approval_id")
    _require_token(approval.record_revision, "approval.record_revision")
    _require_token(approval.policy_version, "approval.policy_version")
    _validated_action(approval.action)
    return approval


def _validated_command(command: object) -> Command:
    if type(command) is not Command:
        raise TypeError("command must be a Command")
    _require_token(command.approval_id, "command.approval_id")
    _require_token(command.expected_record_revision, "command.expected_record_revision")
    _require_token(command.policy_version, "command.policy_version")
    _require_token(command.idempotency_key, "command.idempotency_key")
    _validated_action(command.action)
    return command


@dataclass(frozen=True)
class ApprovedAction:
    """Action identity with sorted, immutable string parameters."""

    operation: str
    target_id: str
    parameters: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        _require_token(self.operation, "action.operation")
        _require_token(self.target_id, "action.target_id")
        object.__setattr__(self, "parameters", _canonical_parameters(self.parameters))

    def snapshot(self) -> ApprovedAction:
        _validated_action(self)
        return ApprovedAction(self.operation, self.target_id, tuple(self.parameters))


@dataclass(frozen=True)
class Approval:
    """Trusted application-owned approval captured against state and action."""

    approval_id: str
    action: ApprovedAction
    record_revision: str
    policy_version: str

    def __post_init__(self) -> None:
        _require_token(self.approval_id, "approval.approval_id")
        _require_token(self.record_revision, "approval.record_revision")
        _require_token(self.policy_version, "approval.policy_version")
        action = _validated_action(self.action)
        object.__setattr__(self, "action", action.snapshot())

    def snapshot(self) -> Approval:
        _validated_approval(self)
        return Approval(
            self.approval_id,
            self.action.snapshot(),
            self.record_revision,
            self.policy_version,
        )


@dataclass(frozen=True)
class Command:
    """A request to execute an already approved action."""

    approval_id: str
    action: ApprovedAction
    expected_record_revision: str
    policy_version: str
    idempotency_key: str

    def __post_init__(self) -> None:
        _require_token(self.approval_id, "command.approval_id")
        _require_token(self.expected_record_revision, "command.expected_record_revision")
        _require_token(self.policy_version, "command.policy_version")
        _require_token(self.idempotency_key, "command.idempotency_key")
        action = _validated_action(self.action)
        object.__setattr__(self, "action", action.snapshot())

    def snapshot(self) -> Command:
        _validated_command(self)
        return Command(
            self.approval_id,
            self.action.snapshot(),
            self.expected_record_revision,
            self.policy_version,
            self.idempotency_key,
        )


@dataclass(frozen=True)
class Write:
    """One independently snapshotted in-memory side effect."""

    approval_id: str
    idempotency_key: str
    action: ApprovedAction

    def __post_init__(self) -> None:
        _require_token(self.approval_id, "write.approval_id")
        _require_token(self.idempotency_key, "write.idempotency_key")
        action = _validated_action(self.action)
        object.__setattr__(self, "action", action.snapshot())


@dataclass(frozen=True)
class CommandResult:
    status: Literal["review", "executed", "deduplicated"]
    reason: str


@dataclass
class InMemoryCommandBoundary:
    """Apply a small command contract to validated, in-memory state."""

    current_permission: bool
    current_record_revision: str
    current_policy_version: str
    approval: Approval
    state: Literal["approved", "review", "executed"] = field(default="approved", init=False)
    writes: list[Write] = field(default_factory=list, init=False)
    _completed_by_key: dict[str, Command] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        self._validate_current_state()
        approval = _validated_approval(self.approval)
        self.approval = approval.snapshot()

    def execute(self, command: Command) -> CommandResult:
        """Validate first, then execute once or return a prior idempotent result."""
        try:
            _validated_command(command)
            self._validate_current_state()
            _validated_approval(self.approval)
        except (TypeError, ValueError):
            return self._review("malformed_input")

        completed = self._completed_by_key.get(command.idempotency_key)
        if completed is not None:
            if completed == command:
                return CommandResult("deduplicated", "already_executed")
            return self._review("idempotency_key_conflict")

        if self.state != "approved":
            return CommandResult("review", "approval_not_current")

        reason = self._rejection_reason(command)
        if reason is not None:
            return self._review(reason)

        self.writes.append(
            Write(
                approval_id=self.approval.approval_id,
                idempotency_key=command.idempotency_key,
                action=command.action.snapshot(),
            )
        )
        self._completed_by_key[command.idempotency_key] = command.snapshot()
        self.state = "executed"
        return CommandResult("executed", "in_memory_write_recorded")

    def _validate_current_state(self) -> None:
        if type(self.current_permission) is not bool:
            raise TypeError("current_permission must be a boolean")
        _require_token(self.current_record_revision, "current_record_revision")
        _require_token(self.current_policy_version, "current_policy_version")

    def _review(self, reason: str) -> CommandResult:
        if self.state == "approved":
            self.state = "review"
        return CommandResult("review", reason)

    def _rejection_reason(self, command: Command) -> str | None:
        if command.approval_id != self.approval.approval_id:
            return "approval_mismatch"
        if self.current_permission is not True:
            return "permission_revoked"
        if command.expected_record_revision != self.approval.record_revision:
            return "approved_record_revision_mismatch"
        if self.current_record_revision != self.approval.record_revision:
            return "current_record_revision_mismatch"
        if command.policy_version != self.approval.policy_version:
            return "approved_policy_version_mismatch"
        if self.current_policy_version != self.approval.policy_version:
            return "current_policy_version_mismatch"
        if command.action != self.approval.action:
            return "approved_action_mismatch"
        return None
