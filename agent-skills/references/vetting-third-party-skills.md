# Vetting third-party skills before you run them

> How to review a skill you did not author — or one your agent generated for you — before giving it the permissions your agent has.

A skill is not a document you read; it is **executable capability**. When an agent activates a skill, the skill's instructions and scripts run with the agent's own permissions: shell access, read/write to the file system, credentials from environment variables and config files, and the ability to send messages. Installing an unvetted skill is like installing a package from a registry you have never heard of, except that no package manager gate exists by default.

The risk is not theoretical. Snyk's ToxicSkills audit (published February 2026) scanned 3,984 skills from ClawHub and skills.sh, the largest public corpus of agent skills then known:

- **13.4% (534) contained at least one critical-level issue** — malware, prompt injection, or exposed secrets.
- **36.82% (1,467) had at least one security flaw at any severity** — hardcoded API keys, insecure credential handling, or dangerous third-party content exposure.
- **76 confirmed malicious payloads** were found, with credential theft, backdoor installation, and data exfiltration; 8 were still publicly available at publication.

Source: [Snyk — ToxicSkills: Snyk finds malware and prompt injection in 36% of AI agent skills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/). The open Agent Skills standard says nothing about whether a given skill is safe; treat "published in a registry" as zero security signal.

## When to use this reference

Use it whenever you are about to **run** a skill you did not author and have not previously vetted:

- A skill pulled from a public registry or marketplace (skills.sh, ClawHub, or similar).
- A skill shared by a colleague, copied from a blog post, or vendored from another repository.
- A skill an LLM generated for you in one pass and you have not read.
- An updated version of a third-party skill you already run — re-vet on material version changes.

It also applies to skills embedded in repositories you clone: project-level skills from an untrusted repository can inject instructions into your agent's context (see `client-implementation.md` for the client-side trust-gating angle).

## The vetting checklist

Work through this before the first run. It is a dependency review, not a skim.

### 1. Provenance

- Who published it, and when? Is the author identifiable, with a history beyond the skill itself? A registry account that is days old is a red flag.
- Does it have a license, a README, a changelog? Does the repository look maintained or abandoned?
- How did you obtain it? A direct link from a trusted source you already rely on is different from a search-result download.
- Prefer pinned versions and record what you installed, so you can diff later updates.

### 2. The SKILL.md itself

Read the whole file — not just the description. The description is marketing; the body is the contract.

- Does the body's actual behavior match the description's promise?
- Look for hidden or deceptive instructions: base64 or other obfuscation, Unicode smuggling, "ignore previous instructions" patterns, system-message impersonation, instructions to do something unrelated to the stated purpose (e.g., a "weather" skill that tells the agent to read files in `~/.ssh`).
- Does it instruct the agent to fetch and follow remote content at runtime? That is indirect prompt injection — the remote author gains control over your agent.
- Does it ask the agent to print, echo, or reveal credentials, API keys, or tokens?

### 3. Every script and executable

Scripts run with your agent's permissions. Read each one before it ever executes.

- **Network calls**: what hosts does it reach out to? Unknown domains, IP-literal URLs, typosquatted package names, `curl | bash` patterns, and password-protected archives are red flags.
- **File system access**: does it read or write outside its own skill directory? Pay special attention to dotfiles, SSH keys, shell profiles, credential stores, and config files.
- **Credential handling**: hardcoded secrets, keys passed on command lines, instructions to store secrets in plaintext.
- **Dynamic behavior**: remote imports, downloads that execute, obfuscated or minified code you cannot read.
- **Dependencies**: are they named, pinned, and from known sources? Executables requiring elevated privileges deserve extra scrutiny.

### 4. References and assets

Files in `references/` and `assets/` can carry instructions too. Scan them for the same patterns as the SKILL.md: remote fetching, hidden instructions, secrets.

## Safe first-run practice

Even after a clean review, run it the way you would run any untrusted dependency the first time:

- Run in a sandboxed environment (container, VM, or disposable profile) where the agent has no real credentials.
- Run with an empty or minimal environment — no production API keys, no personal tokens.
- Prefer read-only access to the file system where the harness supports it.
- Watch what it actually does before granting it your real working context.

## If you find a problem

- Do **not** run the skill further, and do not "fix and continue" silently.
- Report it: the registry or marketplace the skill came from, and the author if contactable. Malicious skills are a supply-chain incident, not a code review finding.
- If the skill is part of a dependency chain you already run, treat discovery like any other vulnerability: assess exposure, rotate any credentials the skill could have seen, and record what you know.

## Gotchas

- **An open standard is not a safety standard.** Format compliance says nothing about intent. A perfectly schema-valid SKILL.md can be malware.
- **Curation is not an audit.** A "top skills" list measures popularity, not safety.
- **LLM-generated skills need the same review as stranger's skills.** The model that wrote the skill is not a security reviewer, and generated skills often contain plausible-looking but unverified instructions.
- **Re-vet on updates.** A skill you vetted at v1.0 is a new dependency at v2.0. Diff the change before letting it back in.
