# AutoGen FAQ and Troubleshooting

## Installation

**Q: Which version should I install?**
A: The examples in this skill target AgentChat 0.7.5 on Python 3.10+. From this skill directory run `python -m pip install -r requirements.txt`. `pyautogen` 0.2 is a separate legacy API and its examples are labeled as such.

**Q: Docker not available?**
A: Use `LocalCommandLineCodeExecutor` for development, but understand the security risks.

## Migration

**Q: Code from v0.2 doesn't work?**
A: v0.4 has breaking API changes. See the migration guide at https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/migration-guide.html.

## Common Errors

**Q: A team keeps running?**
A: Give the team a termination condition such as `MaxMessageTermination` or `TextMentionTermination`; `is_termination_msg` is a legacy `pyautogen` 0.2 parameter.

**Q: UserProxyAgent waits for input?**
A: That is its purpose in AgentChat: it represents a human and calls `input_func`. Supply the right input function or use an automated agent when there is no human participant.

**Q: Nested chat never returns?**
A: Ensure `CancellationToken` is passed and not already cancelled.

**Q: Code execution fails?**
A: Docker must be running for Docker executor. Use `LocalCommandLineCodeExecutor` for local dev.

**Q: GroupChat speaker selection is wrong?**
A: Use `RoundRobinGroupChat` for fixed order if `SelectorGroupChat` picks poorly.

## Performance

**Q: High token usage?**
A: Each agent-to-agent message consumes tokens. Set `max_turns` conservatively.
