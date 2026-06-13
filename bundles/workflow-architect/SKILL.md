1|---
2|name: workflow-architect
3|description: >-
4|  Discover your actual workflow through conversation or observation, then generate
5|  a tailored skills bundle that encodes it as loadable agent skills with trigger
6|  conditions. Use when you want to understand your own process, formalize it, or
7|  share it with collaborators. Also use when a session feels aimless — this skill
8|  gives it structure.
9|license: MIT
10|compatibility: >-
11|  Hermes Agent — uses skill_view(), memory tool, session context scanning,
12|  and write_file for bundle generation. Output bundles are standard Agent Skills.
13|metadata:
14|  tags: [workflow, meta, productivity, skills-bundle, onboarding, process]
15|  spec-version: "1.0"
16|---
17|
18|# Workflow Architect
19|
20|A meta-skill that helps you (and your agent) understand how you actually work. It
21|discovers your workflow patterns through either active interrogation or passive
22|observation, then generates a **skills bundle** — a set of loadable skills, each
23|with trigger conditions, that encode your workflow so your agent can meet you
24|where you are in every session.
25|
26|## What You Get
27|
28|After running workflow-architect, you'll have a new bundle in your agent's skill
29|directory containing:
30|
- **Umbrella SKILL.md** — the entry point that makes the bundle auto-detectable
  via trigger conditions in its description. Load it with `skill_view(name='<bundle-name>')`
  or let the agent discover it automatically when you say something matching its triggers.
39|- **Sub-skills** — one per phase of your workflow, each with a `description`
40|  that tells the agent when to load it (e.g., "load this when the user starts
41|  their morning triage routine" or "use this when the user shifts into deep work
42|  mode")
43|- **A manifest** — maps skill names to their trigger conditions, entry points,
44|  and transition signals
45|- **A decision map** — Mermaid flowchart visualizing your workflow as the agent
46|  sees it
47|- **A kanban board** (optional) — only included if your workflow follows a
48|  predictable linear path where WIP limits and lane transitions add value
49|
The umbrella and sub-skills are registered via `skill_manage(action='create')`
so they appear in `skills_list()` and are immediately loadable in future sessions.
59|
60|## Two Modes
61|
62|Workflow-architect adapts to how you want to engage with it.
63|
64|### Mode 1: Active Interrogation (One-Shot)
65|
66|**When to use:** You have a few minutes to talk through your process. This is
67|the most thorough mode — the agent asks guided questions, branches based on your
68|answers, and builds a model of your workflow turn by turn.
69|
70|**How to invoke:**
71|```
72|/workflow-architect
73|```
74|
75|The agent will guide you through a conversation of about 8-15 questions.
76|Answer naturally — the skill adapts its probes based on what you say.
77|
78|### Mode 2: Passive Observation
79|
80|**When to use:** You're already in a session doing real work and don't want to
81|stop and reflect. Let this mode watch what you actually do, then infer the
82|workflow pattern from your actions.
83|
84|**How to invoke:**
85|```
86|/workflow-architect passive
87|```
88|
89|The agent loads the observer skill silently. It does nothing until you say one
90|of the trigger phrases below, at which point it scans the current session's
91|message history and reconstructs your workflow from what happened.
92|
93|**Trigger phrases (say any of these to activate observation analysis):**
94|- "catalog my workflow"
95|- "what's my workflow"
96|- "analyze my process"
97|- "figure out what I do"
98|- "work it out from what I just did"
99|
100|> **Limitation:** Observation mode works best after a session with at least
101|> 20+ turns of substantive work. If the session context is too thin, the
102|> observer will suggest switching to active interrogation mode instead.
103|
104|## Loading Protocol
105|
106|1. Read this umbrella SKILL.md for context
107|2. If active: load `skills/interviewer/SKILL.md`
108|3. If passive: load `skills/observer/SKILL.md`
109|4. After convergence: load `skills/bundle-builder/SKILL.md` to synthesize
   and write the output bundle. The bundle is written to
   `~/.hermes/skills/<category>/<bundle-name>/` — verify the umbrella loads
   with `skill_view(name='<bundle-name>')` and at least one sub-skill loads
   with `skill_view(name='<bundle-name>-<phase-name>')`. Tell the user where
   it landed, what skills it contains, and a trigger phrase they can use to
   enter the workflow.
123|
124|## What the Interview Builds
125|
126|The interviewer (and observer, through inference) builds a structured model
127|with these dimensions:
128|
129|| Dimension | What it captures |
130||-----------|------------------|
131|| **Entry points** | How your sessions typically start |
132|| **Phases** | The distinct modes or stages in your workflow |
133|| **Branching signals** | What makes you go left vs right at each fork |
134|| **Tool preferences** | What you reach for in each phase |
135|| **Loop conditions** | What keeps you in a mode vs what kicks you out |
136|| **Exit criteria** | How you know a session is done |
137|| **Pain points** | What feels frictionful or inefficient |
138|
139|## Environment
140|
141|No environment variables required. State is stored via memory tool
142|with the prefix `workflow-architect:state:` so it persists across turns
143|during multi-turn interviews.
144|