# HarnessKit

[简体中文](README.md) | **English**

**Stop explaining your codebase from scratch in every AI session.**

Let Codex read your code and document its architecture, features, and interface contracts. Keep that knowledge current as the code changes, and check for missing, misplaced, or stale documentation. Everything lives in your repository as Markdown that future tasks can read when needed.

Use it to understand an existing codebase, carry context across sessions, or set up a knowledge structure for a new project.

**The idea: ground the work in evidence, guide it with rules, verify the results, and keep what you learn.** Confirmed knowledge becomes the starting point for the next task.

[Quick start](#quick-start) · [Four skills](#four-skills) · [How it works](#how-it-works) · [FAQ](#faq) · [Contributing](#contributing)

![HarnessKit workflow: discover source evidence, maintain project knowledge, and audit without editing. Skill updates are separate from project documentation.](assets/workflow.svg)

## What it solves

AI can write code, but context is easy to lose between sessions. Interface boundaries need explaining again, documentation drifts from the implementation, and generated templates may look complete without helping anyone make the next change.

| Problem | How HarnessKit helps |
| --- | --- |
| Repeating project context every session | A short AGENTS.md provides rules; an index routes the agent to relevant knowledge |
| Detailed documentation without evidence | Trace real entry points and call chains; link important claims to source files and symbols |
| Documentation falls behind new features | Update the relevant Feature or Spec, its index entry, and verification records |
| Contracts buried in indexes, missing entries, broken links | Scripts check structure; the agent reviews content responsibilities and evidence |
| Tool updates might overwrite project knowledge | Installed skills and project documentation have separate update paths |

## Why HarnessKit

- **Start with code.** Inspect source, build configuration, and tests before documenting an existing project. Use a scaffold only when there is no application code.
- **Keep knowledge in the repository.** Plain Markdown is searchable, reviewable, and versionable. No online Page is required at runtime.
- **Keep instructions predictable.** New AGENTS.md rules come from a strict template. Architecture, feature behavior, and shared contracts have distinct homes.
- **Maintain existing topics.** Update rather than duplicate documents. Separate implementation facts, plans, and open questions.
- **Audit without changing files.** Report problems first. No automatic content migration or project edits.

HarnessKit currently targets **Codex**. Its document structure is not tied to a programming language. Accurate documentation still requires source investigation and review; these skills cannot guarantee that an agent will catch every detail.

## Quick start

### 1. Install the four skills

Send this in a Codex environment that supports Skills:

```text
Use $skill-installer to install these four skills from the main branch of lugq/harness-kit:
skills/harness-init
skills/harness-spec
skills/harness-check
skills/harness-update
```

Helper scripts require **Python 3.9+**. Updating skills also requires **Git**. In a subsequent turn, type `$harness-` to select a skill. If the list has not refreshed, reopen the conversation or restart the client. Installation is local to the execution environment; it does not sync across machines.

### 2. Initialize a project

Open the target project and send:

```text
$harness-init Inspect the actual code and create project knowledge documents.
Preserve existing materials and uncommitted changes. Write the documents in English.
```

If a knowledge directory already exists, agree on the scope before writing. Existing materials are not automatically overwritten or migrated. Applicable project instructions still apply; other pre-existing documents are initialization sources only when explicitly requested.

### 3. Maintain documentation and check it

```text
$harness-spec Document the video export feature from the actual code.
Update an existing topic if present, register new documents in the index,
and update affected shared contracts. Do not change application code.
Write the documents in English.
```

```text
$harness-check Audit this project's Harness documentation.
Report findings in English. Do not change any files.
```

These are **Codex skill invocations**, not terminal commands. Maintenance registers new documents and updates existing topics. An audit does not apply fixes or append verification records.

The skill instructions, bundled templates, and some script messages are currently in Chinese. This README provides English usage examples; it does not mean every bundled resource has been translated. The strict AGENTS.md template is copied in its current language rather than freely translated.

## Four skills

| Skill | When to use it | Output and scope |
| --- | --- | --- |
| [harness-init](skills/harness-init/SKILL.md) | Establish project knowledge for the first time | Inspect code and create instructions and documents while protecting existing content |
| [harness-spec](skills/harness-spec/SKILL.md) | Capture a new feature, contract change, or discovery | Maintain related documents, indexes, and actual verification records; no feature implementation |
| [harness-check](skills/harness-check/SKILL.md) | Review accumulated documentation issues | Read-only findings about structure, misplaced content, and evidence gaps |
| [harness-update](skills/harness-update/SKILL.md) | Get a newer HarnessKit version | Update installed skills without changing project documents |

## How it works

### Initialize: map the code, collect evidence, document contracts

Locate modules, public entry points, build configuration, and tests. Follow inputs, state, outputs, failures, and resource cleanup. Feature documents describe specific capabilities; Spec documents describe shared technical contracts. Important claims link to supporting code instead of relying on filled-in templates.

The default layout looks like this. Actual feature and technical topics come from the project; the example filenames below are not bundled functionality:

```text
AGENTS.md                       # Stable working rules and knowledge entry point
.harness/
├── index.md                    # Paths, purposes, and when to read each document
├── architecture.md             # Module responsibilities, dependencies, boundaries
├── verification.md             # Source baseline, investigation scope, actual checks
├── features/
│   ├── README.md               # Writing guidance
│   └── video-export.md         # Example topic, not a prebuilt feature
├── specs/
│   └── resource-lifecycle.md   # Example topic, not a preset project contract
└── decisions/
    └── README.md               # Add decisions only with confirmed supporting context
```

Empty projects receive a scaffold with unconfirmed architecture and a default specs/development.md. Default working agreements are labeled as such; they are not presented as findings from code.

### Maintain: check for lasting knowledge after a change

After relevant verification has a result and before the final completion report, check whether the change introduced lasting knowledge or invalidated an existing document. Update Features for behavior changes, Specs for shared contracts, and architecture for module boundary changes. Leave documents alone when nothing needs updating.

This depends on the agent following project rules. **There is no hook that enforces automatic write-back.** Invoke `$harness-spec` explicitly when needed. Mark planned functionality as unimplemented. Distinguish executed checks, cache hits, missing test sources, and skipped checks; never report an unperformed acceptance test as passed.

### Audit: separate definite errors from review findings

The structural script checks index reachability, duplicate entries, missing purposes or reading conditions, and local inline links. The agent then reviews whether indexes contain detailed contracts, whether Feature and Spec responsibilities overlap, and whether important claims have evidence.

Length, TODO markers, and open questions are not errors by themselves. Source consistency requires reading the relevant code. External URLs, anchors, and complex Markdown are not fully covered by the structural script. Reports must state what was and was not checked.

## Updates and older installations

```text
$harness-update
```

The updater checks installation state, stages and validates incoming packages, then replaces the skills. Ordinary failures roll back. Local edits, extra files, and unrecognized installations block replacement. If a standard installation has no baseline, the updater checks complete file hashes against the repository's main-branch history.

Older updaters know only the skills available at the time: update the existing skills, then invoke the new `$harness-update` once more to install a missing harness-spec or harness-check. Skill updates do not overwrite existing project documents.

Downloads use HTTPS by default, with existing Git credentials or a GitHub CLI login. The script accepts `--repo` for a trusted SSH/HTTPS repository and does not change global Git configuration.

For advanced use, pass `--check` to the update script for a dry check. After a forced interruption, first ensure no other updater is running, then use `--recover` to restore or clean up the transaction. Backups remain until completion. Replacing multiple directories is not a single atomic operation, and recovery does not cover disk corruption.

## FAQ

**Will it overwrite an existing AGENTS.md?**

Existing text is preserved. Only missing template rules are added verbatim; semantically equivalent rules are skipped. The only permitted template substitution is the agreed knowledge-directory path. If you choose to preserve the entry point, the entire file stays unchanged.

**Is .harness required?**

It is the default for new projects. An existing custom entry point can be retained. Migration requires explicit authorization; other directories keep their project-defined responsibilities.

**Will an audit fix problems?**

By default, it only reports them. Apply changes through a separate maintenance request with an explicit scope.

**Will it read all my old materials or commit my code?**

Initialization does not automatically import other memory or specification systems. Maintenance reads relevant knowledge only. Project knowledge workflows do not automatically commit, push, install dependencies, or implement application features.

## Contributing

Issues with reproducible examples and pull requests improving workflows, templates, or checks are welcome. Include a minimal directory layout, the invocation, expected behavior, and actual results. Remove sensitive information from examples.

Repository layout: `skills/` contains four independently installable skills, `tests/` contains standard-library regression tests, and `assets/` contains presentation resources.

Before submitting a change, run:

```bash
python3 -m unittest discover -s tests -v
```

Tests cover strict templates, index registration and links, read-only auditing, installation upgrades, local-edit protection, and failure recovery. Skill changes should also pass skill-creator's `quick_validate.py`; it validates formatting, not behavior. Keep the Feature and Spec templates in init/spec synchronized; a test checks their equality.

## Acknowledgments

The investigate-first approach draws on [Trellis Spec Bootstrap](https://github.com/mindfold-ai/Trellis/tree/main/.agents/skills/trellis-spec-bootstrap). HarnessKit adapts the workflow to its own scope. It does not depend on Trellis or include its full task-management system.
