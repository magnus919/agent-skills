# AutoGen FAQ and Troubleshooting

## Installation

**Q: Which version should I install?**
A: `pip install autogen-agentchat` for the current v0.4+ API. The older `pip install pyautogen` installs v0.2 (deprecated).

**Q: Docker not available?**
A: Use `LocalCommandLineCodeExecutor` for development, but understand the security risks.

## Migration

**Q: Code from v0.2 doesn't work?**
A: v0.4 has breaking API changes. See the migration guide at https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/migration-guide.html.

## Common Errors

**Q: Agent loops forever?**
A: Set `is_termination_msg` or `max_turns`. The agent needs a termination condition.

**Q: UserProxyAgent keeps asking for input?**
A: `human_input_mode` defaults differently. Set to "NEVER" for automated execution.

**Q: Nested chat never returns?**
A: Ensure `CancellationToken` is passed and not already cancelled.

**Q: Code execution fails?**
A: Docker must be running for Docker executor. Use `LocalCommandLineCodeExecutor` for local dev.

**Q: GroupChat speaker selection is wrong?**
A: Use `RoundRobinGroupChat` for fixed order if `SelectorGroupChat` picks poorly.

## Performance

**Q: High token usage?**
A: Each agent-to-agent message consumes tokens. Set `max_turns` conservatively.
