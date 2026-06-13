1|---
2|name: bundle-builder
3|description: >-
4|  The synthesis engine for workflow-architect. Reads accumulated workflow
5|  state from memory and renders it into a valid Agent Skills bundle directory
6|  with sub-skills, manifest, decision map, and optional kanban board. Loaded
7|  after the interviewer or observer achieves convergence.
8|license: MIT
9|compatibility: Hermes Agent — uses write_file for bundle output, shell_quote
10|metadata:
11|  tags: [workflow, generation, bundle, synthesis]
12|  spec-version: "1.0"
13|---
14|
15|# Bundle Builder — Workflow Synthesis Engine
16|
17|This sub-skill is loaded after the interviewer (active mode) or observer
18|(passive mode) achieves convergence. It reads the accumulated workflow
19|state from memory and generates an output bundle directory.
20|
21|## Input
22|
23|All `workflow-architect:state:*` memory entries. Read them all at once:
24|
25|```
26|Read: workflow-architect:state:entry_points
27|Read: workflow-architect:state:phases
28|Read: workflow-architect:state:branching
29|Read: workflow-architect:state:pain_points
30|Read: workflow-architect:state:exit_criteria
31|```
32|
33|If any required fields are missing (entry_points, phases, branching, exit_criteria),
34|abort with a clear message about what's missing.
35|
36|## Output Structure
37|
38|The bundle is written to `~/.hermes/skills/<category>/<bundle-name>/` with this layout:
39|
40|```
41|<bundle-name>/
├── SKILL.md                # *** UMBRELLA ENTRY POINT *** — makes the bundle
│                           # loadable via skill_view() and discoverable by
│                           # the agent's skill scanner on trigger keywords.
│                           # CRITICAL: without this, the bundle is invisible.
50|├── README.md               # Summary of this bundle
51|├── manifest.yaml           # Skill-to-trigger mapping
52|├── skills/
53|│   ├── entry-skill.md      # One per discovered phase
54|│   ├── phase-two.md
55|│   └── ...
56|├── decision-map.md         # Mermaid flowchart
57|├── AGENTS.md               # Agent loading instructions for this bundle
58|├── kanban/
59|│   └── board-definition.yaml  # Only if kanban is appropriate
60|└── references/
61|    └── generated-from.md   # Metadata about how this bundle was created
62|```
63|
**The `SKILL.md` umbrella is not optional.** Without it, individual sub-skills
may exist on disk but the agent's skill scanner has no entry point to match
trigger keywords against. The umbrella is how the agent discovers and enters
the bundle.
74|
75|### Bundle naming
76|
77|Ask the user for a bundle name at the start of synthesis:
78|
79|```
80|"Before I generate the bundle — what should I call it?
81|Something short, lowercase with hyphens, like 'my-triage-workflow'
82|or 'dev-sprint-routine'."
83|```
84|
85|Fallback if user doesn't provide one: `my-workflow-<archetype>-<date>`.
86|
87|### Writing the files
88|
89|For each file in the output bundle, use the templates in `templates/` as
90|starting points. Render them by substituting the state values.
91|
92|**Step-by-step file creation order:**
93|
0. **Umbrella SKILL.md** — **MANDATORY FIRST STEP.** This is the entry point
   that makes the bundle discoverable. Write it directly to the bundle directory
   as `SKILL.md`, then register it via `skill_manage(action='create')`.

   The umbrella must include:

   - `name: <bundle-name>` matching the bundle name
   - `description` with **broad trigger keywords** covering all common ways the
     user enters this workflow (e.g., "I want to write about X", "I read
     something interesting", "can you research this", "draft it", "ship it")
   - `compatibility: Hermes Agent`
   - `metadata.tags` including `workflow`, `bundle`, and domain-relevant tags

   Body content:

   ```markdown
   # <Bundle Name>

   A <N>-phase workflow covering <brief summary>.

   ## Pipeline

   <Phase 1> → <Phase 2> → <Phase 3> → ...

   (Include a Mermaid flowchart graph LR showing the phase sequence.)

   ## Sub-Skills

   | Phase | Skill | Trigger |
   |-------|-------|---------|
   | <name> | `<bundle-name>/<phase-file>` | <when to load> |
   | ... | ... | ... |

   ## Navigation

   When you load this umbrella, identify which phase the user is in,
   load the corresponding sub-skill via skill_view(), and follow its
   instructions. Use the transition signals in each sub-skill to know
   when to move to the next phase.

   ## Pipeline Heuristics

   - Can the user enter at any phase, or must they start at Phase 1?
138|   - Are any phases automatic (e.g., refine always follows draft)?
139|   - What's the relationship between phases (sequential, branching, optional)?
140|   ```
141|
142|   **Category choice:** Place the bundle in a category that matches where its
143|   sub-skills live (e.g., `content` for blogging pipelines, `devops` for
144|   deployment workflows). Ask the user if unsure.
145|=======
146|0. **umbrella SKILL.md** — Create the bundle's entry point. This is the
147|   first file because the umbrella must be registered and discoverable
148|   before any sub-skill can be loaded.
149|
150|   a. Generate an umbrella SKILL.md with:
151|
152|      **Frontmatter:**
153|      - `name: <bundle-name>`
154|      - `description:` — Craft this carefully. Include broad trigger
155|        phrases that cover all phases of the workflow, so the agent can
156|        auto-detect this bundle in future sessions. Pattern:
157|        "Use when [trigger summary]. Covers: [phase list]."
158|      - `tags: [workflow, bundle:generated, <archetype>]`
159|      - `spec-version: "1.0"`
160|
161|      **Body:**
162|      - H1: `# <Bundle Name>` (user-friendly title)
163|      - **Phase table** — Markdown table mapping each sub-skill
164|        name to its trigger condition and typical entry signal.
165|        Columns: | Phase | Load this skill | When |
166|      - **Workflow flowchart** — Mermaid `graph LR` or `graph TD`
167|        showing entry → phases (with decision diamonds for
168|        branching) → exit. Entry condition links to the description.
169|      - **Navigation instructions** — Explain the two-entry model:
170|        (1) auto-detect via trigger conditions, (2) `skill_view(name='<bundle-name>')`
171|        to inspect the pipeline. Tell the agent: identify the user's
172|        current phase, load that sub-skill, follow its instructions.
173|      - **Heuristics** — Phase ordering notes (sequential vs. flexible),
174|        entry points (can start at any phase), transition signals.
175|
176|   b. Write to `<bundle-name>/SKILL.md` via `write_file`.
177|
178|   c. Register with:
179|      ```
180|      skill_manage(action='create', name='<bundle-name>', content='...')
181|      ```
182|
183|   > **Why step 0?** The umbrella SKILL.md is the agent's entry point to
184|   > the entire bundle. It must exist and be registered first so that any
185|   > subsequent sub-skill loading instructions reference a discoverable
186|   > parent. Without it, the bundle is invisible to the agent.
187|>>>>>>> 77f9d16 (fix(bundle-builder): generate umbrella SKILL.md as discoverable entry point)
188|
189|1. **manifest.yaml** — Use `templates/manifest.yaml.tmpl`. Substitute:
190|   - `{{BUNDLE_NAME}}` — the bundle name
191|   - `{{PHASES}}` — each phase with its trigger keywords, entry signals,
192|     typical tools, and exit signals
193|   - `{{HAS_KANBAN}}` — true/false based on kanban decision
194|
195|2. **README.md** — Write from scratch (no template needed, it's prose).
196|   Structure:
197|
198|   ```markdown
199|   # <Bundle Name>
200|
201|   Generated by workflow-architect on <date>.
202|
203|   This bundle covers a <archetype>-style workflow with <N> phases.
204|
205|   ## Skills
206|
207|   | Skill | Trigger | When it fires |
208|   |-------|---------|---------------|
209|   | <name> | <trigger description> | <when to load> |
210|
211|   ## Loading
212|
213|   Skills in this bundle are loaded automatically by trigger conditions.
214|   To load a specific skill: `skill_view(name='<bundle-name>/<skill-name>')`
215|
216|   ## Kanban
217|
218|   (Only if kanban exists) This workflow maps to a kanban board with <N> lanes.
219|   ```
220|
221|3. **Sub-skills** — For each phase in `workflow-architect:state:phases`,
222|   generate a `.md` file in `skills/` using `templates/skill-skeleton.md`.
223|
224|   Naming convention: `kebab-case-phase-name.md` (e.g., `morning-triage.md`).
225|
226|   Each sub-skill file is a valid Agent Skills SKILL.md with:
227|   - `name` matching the filename (without .md)
228|   - `description` that includes trigger keywords from the phase's typical
229|     openers and tools
230|   - `compatibility: Compatible with any agent supporting the Agent Skills format`
231|   - Body sections:
232|     - **When to use** — the trigger condition in natural language
233|     - **What to do** — step-by-step instructions for the agent in this phase
234|     - **Transition signals** — what the user typically says or does that
235|       transitions out of this phase
236|     - **What to tell the user** — guidance on how the agent should communicate
237|       during this phase
238|
239|4. **decision-map.md** — Use `templates/decision-map.md.tmpl`. Substitute:
240|   - `{{WORKFLOW_NAME}}` — bundle name
241|   - `{{PHASE_NODES}}` — phase names
242|   - `{{BRANCHING}}` — decision diamonds
243|   - `{{ENTRY}}` — how sessions start
244|   - `{{EXITS}}` — how sessions end
245|
246|5. **AGENTS.md** — Standard agent loading instructions for this bundle.
247|   Short — just says which skills exist and when to load them.
248|
249|6. **kanban/ directory** — Only if the kanban-decision-criteria.md reference
250|   indicates kanban is appropriate. Generates three files:
251|
252|   a) **kanban/board-setup.sh** — Use `templates/kanban-board-setup.sh.tmpl`.
253|      Substitutes:
254|      - `{{BOARD_SLUG}}` — bundle name (kebab-case)
255|      - `{{BOARD_NAME}}` — title-case version or user-provided name
256|      - `{{FIRST_PHASE_SKILL}}` — skill file for the first phase
257|      - `{{FIRST_PHASE_PRIORITY}}` — priority for first-phase tasks
258|      - `{{GENERATION_DATE}}` — current date
259|
260|      The setup script creates the board via `hermes kanban boards create`
261|      and prints instructions for adding work.
262|
263|   b) **kanban/task-blueprints.yaml** — Use `templates/kanban-task-blueprints.yaml.tmpl`.
264|      Substitutes:
265|      - `{{BLUEPRINT_ENTRIES}}` — one blueprint entry per phase, each with:
266|        - `phase:` — phase name (kebab-case)
267|        - `title_template:` — e.g. "Build: {{feature}}"
268|        - `skill:` — path to the sub-skill file (e.g. `my-workflow/build`)
269|        - `default_priority:` — descending from first phase (highest) to last
270|        - `initial_status:` — first phase = `todo`, rest = `ready`
271|        - `body:` — instructions for the worker: what skill to load,
272|          definition of done, and transition to next phase
273|
274|   c) **kanban/README.md** — Brief usage guide explaining how to set up and
275|      use the board. Structure:
276|
277|      ```markdown
278|      # Kanban Board: <Bundle Name>
279|
280|      This workflow maps to a Hermes Kanban board with <N> phases in sequence.
281|
282|      ## Setup
283|
284|      Run `kanban/board-setup.sh` to create the board:
285|      ```bash
286|      bash kanban/board-setup.sh
287|      ```
288|
289|      The script creates the board and switches to it. If you prefer to set
290|      it up manually:
291|      ```bash
292|      hermes kanban boards create <bundle-name> --name "<Bundle Name>"
293|      ```
294|
295|      ## Task Lifecycle
296|
297|      <Phase 1> → <Phase 2> → <Phase 3>
298|
299|      Each phase's task depends on the previous phase's task completing.
300|      When a task is done, the next phase's task auto-promotes to "ready"
301|      and the dispatcher picks it up.
302|
303|      ## Adding Work
304|
305|      Create a task for the first phase:
306|      ```bash
307|      hermes kanban create "Build: <feature description>" \\
308|        --skill <bundle-name>/<phase-1-skill> \\
309|        --priority 3
310|      ```
311|
312|      Then create subsequent-phase tasks with `--parent` pointing to the
313|      first task's ID:
314|      ```bash
315|      hermes kanban create "Review: <feature>" \\
316|        --parent <task-id> \\
317|        --skill <bundle-name>/<phase-2-skill> \\
318|        --priority 2
319|      ```
320|
321|      ## Task Blueprints
322|
323|      See `kanban/task-blueprints.yaml` for template definitions of each
324|      phase's task, including default priorities, skill mappings, and
325|      worker instructions.
326|      ```
327|
328|7. **references/generated-from.md** — Metadata about the generation process:
329|
330|   ```markdown
331|   # Generated From
332|
333|   - **Skill:** workflow-architect
334|   - **Mode:** active | passive
335|   - **Date:** <date>
336|   - **Archetype:** <archetype>
337|   - **Convergence Score:** <score>
338|   ```
339|
340|8. **Register sub-skills with Hermes skill system** — For each sub-skill `.md`
341|   file written in step 3, register it so it appears in `skills_list()` and
342|   can be loaded with `skill_view()`. This is the critical step that makes
343|   generated skills actually usable by the agent.
344|
345|   For each sub-skill file in `skills/<name>.md`:
346|
347|   ```python
348|   skill_manage(action='create',
349|       name='<bundle-name>-<skill-name>',
350|       content=read_file('<bundle-path>/skills/<name>.md')['content'],
351|       category='generated')
352|   ```
353|
354|   This creates a proper skill directory with `SKILL.md` entry point, making
355|   the sub-skill discoverable and loadable. The sub-skill's existing valid
356|   Agent Skills frontmatter (name, description, license, tags) is used as-is.
357|
358|   **Why separate registration is needed:** The `skill_manage()` call also
359|   handles the skill directory structure (`SKILL.md` at root, not `<name>.md`
360|   in a `skills/` subdirectory). Without this step, the sub-skill files exist
361|   on disk but no Hermes mechanism discovers them. Only the umbrella SKILL.md
362|   (registered in step 0) would be loadable.
363|
364|   **Verification:** After registering all sub-skills, verify at least one:
365|   ```python
366|   skill_view(name='<bundle-name>-<first-phase-name>')
367|   ```
368|
369|   If it errors, the registration failed — check that the sub-skill file's
370|   frontmatter `name` field matches and the content has valid YAML.
371|
372|## Kanban Decision
373|
374|Before generating kanban files, consult `references/kanban-decision-criteria.md`
375|to decide whether a board is appropriate. The decision depends on the phases
376|and branching structure discovered:
377|
378|- If phases form a clear linear sequence (A → B → C → D), kanban adds value
379|- If branching is emergent (session depends on context), kanban is likely inappropriate
380|- If the user mentioned waiting on others, hand-offs, or status tracking, kanban is a strong fit
381|
382|Present the decision to the user:
383|
384|```
385|"Your workflow has a [linear/emergent] structure. A kanban board [would/wouldn't]
386|add much value here because [reason]. [If yes: I'll add one to the bundle.]"
387|```
388|
389|8. **Register sub-skills** — For each generated sub-skill `.md` file in
390|   `skills/`, register it so Hermes can discover it via `skill_view()` and
391|   `skills_list()`:
392|
393|   ```
394|   For each sub-skill file `skills/<phase-name>.md`:
395|     Read the file content
396|     skill_manage(
397|       action='create',
398|       name='<bundle-name>/<phase-name>',
399|       content=file_content
400|     )
401|   ```
402|
403|   This makes each sub-skill loadable as `skill_view('<bundle-name>/<phase-name>')`.
404|   The bundle name prefix prevents naming collisions with other skills.
405|
406|   If `skill_manage` is not available in the agent's toolset, note this for
407|   the user and suggest they run the registration manually.
408|
409|## Cleanup
410|
411|After writing all files:
412|
413|1. Verify the umbrella registered successfully:
414|   ```
415|   skill_view(name='<bundle-name>')
416|   ```
417|   If it returns `status: available`, proceed. If not found, re-run the
418|   `skill_manage(action='create')` call.
419|
420|2. Remove all `workflow-architect:state:*` memory entries
421|   (`memory(action='remove', target='memory', old_text='workflow-architect:state:')`)
2. Remove all `workflow-architect:state:*` memory entries
   (`memory(action='remove', target='memory', old_text='workflow-architect:state:')`)
2. Tell the user where the bundle was written and what it contains
3. Verify the umbrella loads correctly with `skill_view(name='<bundle-name>')`
   — if it doesn't resolve, check that `skill_manage(action='create')` was run
   and the SKILL.md has valid frontmatter
4. Verify at least one registered sub-skill loads:
   `skill_view(name='<bundle-name>-<first-phase-name>')`
5. Suggest they enter the workflow via any trigger phrase covered by the
   umbrella's description, or by manually loading the umbrella skill
438|