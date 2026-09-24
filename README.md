Student: "Pawan Ratwani-cert-aai-2026-06-0064"
Git Repo: https://github.com/pawan-ratwani/inboxHero

# inboxHero

A local, safety-gated agentic mock-inbox processor for the assignment Parts 1-9.

## Architecture

inboxHero is a small Python orchestration layer rather than a framework-based agent graph.
The flow is:

inbox.json
   |
   v
load + validate messages
   |
   v
high-confidence deterministic rules
   |-----------------------------> rule-resolved decision
   |
   v
local Ollama qwen3.5
(context-dependent classification/reasoning)
   |
   v
thread retrieval + evidence validation
   |
   v
disposition + reason
   |
   +----> reversible action
   |
   +----> irreversible action -> approval/dry-run gate -> outbox
   |
   v
run artifacts -> digest / commitments / thread summaries / dashboard

The system processes the supplied 100-message `inbox.json`. Obvious high-confidence cases
such as receipts, newsletters and no-action notifications are handled by deterministic rules
before a model call. Context-dependent work uses the local Ollama `qwen3.5` model. Every
completed run records its decisions, evidence, security flags and gated actions so that the
outputs can be inspected and reproduced.

## Run

From this directory:

```bash commands
python main.py --cap R1
python main.py --cap R2 --msg m008
python main.py --cap R3 --dry-run
python main.py --cap R4
python main.py --cap R5
python main.py --cap R6
python main.py --cap X1 --sender raghav@paperjet.io
python main.py --cap X2
python main.py --cap X3
python main.py --cap X4 --thread t-launch
```

Run the whole capability set:

```bash commands
python main.py --all
```

The default `python main.py` runs a completed inbox pass and produces the dashboard and Part 8 artifacts.

## Model configuration

The application is intentionally focused on the assignment's **local Ollama model**. Model
settings are loaded by `config.py` from environment variables, with an optional local `.env`
file. No model provider is hardcoded into the application logic.

```
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3.5
OLLAMA_TIMEOUT=60
```

For a local Ollama setup:

```bash
ollama serve
ollama pull qwen3.5
```

If Ollama is unavailable, context-dependent processing fails safe by escalating rather than
inventing a result. Deterministic capabilities that do not require the model can still run.

## Framework choice

**Framework: none.**

CrewAI or Google ADK was not used because inboxHero does not require a multi-agent graph or a
large orchestration framework. Its important control flow is deliberately explicit:

deterministic rules -> model reasoning when needed -> thread/evidence retrieval -> disposition
-> safety gate -> local action/audit.

Keeping this orchestration in ordinary Python makes the security boundary, persistence,
evidence validation and irreversible-action gate straightforward to inspect and test. It also
avoids adding framework behavior that is not required by the problem.

## Disposition vocabulary

Every message receives exactly one disposition:

- **`reply`** — a response is appropriate.
- **`archive`** — no response or further action is needed.
- **`defer`** — legitimate action should happen later or after a condition.
- **`delegate`** — the work should be handed to another person or team.
- **`escalate`** — human attention is required because of ambiguity, risk, authority,
  security, legal/financial consequence, or another safety boundary.

The zeroing invariant is: every input message has exactly one valid disposition and a
non-empty reason; no message is left undecided.

## Retrieval approach

**Retrieval method: thread-walk.**

The inbox already provides `thread_id`, so context-dependent work retrieves all messages in
the relevant thread and orders them chronologically. This keeps the model grounded in the
mail store without introducing an embedding index for a task whose primary context boundary
is already explicit.

For every grounded draft or commitment, evidence message IDs are checked against messages
actually retrieved. If required information is not present in the inbox, inboxHero states that
it is unavailable and does not invent the missing information or draft a reply from it.

## Reversible and irreversible actions

### Reversible / non-delivery actions

- `draft_reply`
- `archive`
- `defer`
- `delegate`
- `escalate`

These do not create an external communication or destroy the mock-mail record.

### Irreversible actions

- `send`
- `delete`

`send` is irreversible because an outgoing message cannot be unsent in this simulation.
`delete` is irreversible because the mock store has no trash or recovery mechanism.

Hostile and phishing messages are **not automatically deleted**. They are flagged and preserved.

## The irreversible-action gate

The gate sits immediately before `send` or `delete`. Every irreversible action requires
explicit human approval. `--dry-run` can be used to show the exact proposed action without
performing it.

For a send, approval results in exactly one JSON message file under `outbox/`. There is no SMTP,
webhook, real mailbox connection or external delivery path.

Every gated decision is recorded with:

1. the proposed action,
2. the human decision, and
3. the resulting action/result.

The escalation boundary is intentionally narrower than "ask the human about everything":
classification and reversible housekeeping can run automatically, while irreversible external
consequences require approval. The trade-off is that some low-risk internal actions may happen
automatically instead of receiving individual approval, reducing approval fatigue while keeping
external/destructive effects under human control.

## Persistent standing instructions

Standing preferences are persisted in `memory.json` and survive process exit/restart. A
preference records its source message ID, and only an authorized owner instruction can establish
or update a standing preference; arbitrary email content cannot grant itself authority.

The demonstrated preference is **m041**: no meetings before 11:00 AM, with earlier proposals
offered at 11:00 AM or later. The affected message is **m043**, which proposes a Monday 09:00
investor meeting. The persistence demonstration stores the preference, exits, starts a fresh
process, reloads `memory.json`, and applies it to m043.

## Hostile inbox handling

Email bodies are untrusted data, not system/developer instructions. Known hostile cases include
m017, m024 and m047. Their embedded requests are refused, flagged and preserved. No corresponding
external forwarding, deletion or other requested action is performed, and the refusal is reported
in the run summary and audit records.

## Capabilities

- **R1 — Zero the inbox (B):** one disposition and reason for every message.
- **R2 — Grounded reply (B):** thread-walk retrieval and verified evidence IDs.
- **R3 — Gate the irreversible (C):** send/delete behind per-action approval or dry-run.
- **R4 — Persistent preference (C):** preference survives a complete process restart.
- **R5 — Refuse embedded instructions (C):** hostile instructions are refused, flagged and preserved.
- **R6 — Dashboard (C):** exactly three panes: pending actions, flagged, commitments.
- **X1 — Unread sender lookup (A):** one deterministic lookup, no model call.
- **X2 — Daily digest (B):** needs you, can wait, and auto-handled sections.
- **X3 — Commitment tracker (B):** structured deadlines/meetings/obligations with evidence.
- **X4 — Open-question thread summary (B):** long-thread state, blocker and unresolved question.

## Outputs and reproducibility

Each completed run creates `runs/<timestamp>/` containing `run.json` and `audit.jsonl`.
Applicable capabilities additionally create:

- `dashboard.html`
- `daily_digest.md`
- `commitments.json`
- `commitments.md`
- `thread_summaries/<thread>.md`

Approved sends write exactly one JSON file per message under `outbox/`. Dry-run never writes
an outbox message. The dashboard and Part 8 outputs are derived from run artifacts rather than
manually assembled.

## Tier coverage

- **Tier A:** X1
- **Tier B:** R1, R2, X2, X3, X4
- **Tier C:** R3, R4, R5, R6

## Final Report

The project materials available to me specify that the final report contains **four answers**,
but the actual four Final Report questions were not included in the supplied files I can access.
I have therefore not invented those answers.

The design facts needed for those answers are documented above: framework choice, thread-walk
retrieval, disposition vocabulary, reversible/irreversible classification, approval gate,
escalation boundary and its trade-off, persistence, hostile-instruction handling, and the
local Ollama architecture.

Provide the four Final Report questions and this section can be completed with the exact answers
without guessing what the assignment asks.
