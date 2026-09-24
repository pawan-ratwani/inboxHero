# CAPABILITIES.md — inboxHero

**Student:** Pawan Ratwani-cert-aai-2026-06-0064  
**Repository:** `<https://github.com/pawan-ratwani/inboxHero>`

Run one capability at a time:

```bash
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

## The system, in one paragraph

inboxHero is a local-only mock-inbox agent. It processes the supplied 100-message `inbox.json`, assigning every message exactly one disposition while routing high-confidence cases through deterministic rules before any model call. Context-dependent work uses the local Ollama `qwen3.5` model. Thread context is retrieved by walking `thread_id` chronologically, and evidence ids are checked against messages actually retrieved. Persistent standing preferences survive process restart in `memory.json`. Irreversible actions are isolated behind an approval gate, and approved sends write only one local file per message under `outbox/`. Hostile instructions embedded in email are treated as untrusted data, refused, flagged and preserved. Completed runs produce machine-readable artifacts that the dashboard and Part 8 capabilities consume.

## Design choices you were asked to state

- **Framework: none.** The system is a deliberately small Python orchestration layer rather than a CrewAI or Google ADK graph. The important control flow is explicit: deterministic routing first, then model reasoning where needed, then retrieval/evidence checks, then disposition and the action-safety gate. This keeps the security boundary, persistence and audit behavior easy to test and inspect.

- **Model: configured through `config.py`.** The assignment requires a local model. The model is used only where language/context reasoning adds value; obvious receipts, newsletters, notifications and other high-confidence cases can be handled without a model call. The run records whether each decision came from a rule or the model and reports how many messages never required a model call.

- **Retrieval: thread-walk.** The inbox already provides `thread_id`, so context-dependent work retrieves all messages in the relevant thread and orders them chronologically. This is more directly grounded in the mock mail store than introducing an embedding index for a task whose primary context boundary is already explicit. If required information is not present in the inbox/thread, the system says it is unavailable and does not invent or draft the missing fact. Every evidence id must correspond to a message actually retrieved.

- **Reversible vs irreversible.** `draft_reply`, `archive`, `defer`, `delegate` and `escalate` are treated as reversible/non-delivery actions. `send` and `delete` are irreversible in this design. A send cannot be unsent in the simulation, and delete has no trash/recovery mechanism. Hostile or phishing messages are not automatically deleted; they remain preserved and flagged.

- **Where the gate sits.** The irreversible-action boundary is immediately before `send` or `delete`. Every such action requires explicit human approval. `--dry-run` is also supported and shows the proposed action without performing it. An approved send creates exactly one file in `outbox/`; there is no SMTP, webhook, or external delivery path. The audit log records the proposed action, the human decision, and the resulting action.

- **Escalation line and trade-off.** The system escalates when the requested action is ambiguous, security-sensitive, financially or legally consequential, beyond the available authority, dependent on missing inbox information, or otherwise crosses a safety boundary. It does not ask the user to approve every ordinary classification, archive, defer or draft. The trade-off is deliberate: some low-risk work is automated and can be wrong in edge cases, while consequential external actions remain under human control. Approval fatigue is reduced without removing the final gate where consequences are hardest to reverse.

- **Standing instructions.** A standing preference is only learned from an authorized owner instruction; an arbitrary email cannot grant itself permission to change safety rules or preferences. The demonstrated preference is **m041**: no meetings before 11:00 AM, with earlier proposals offered 11:00 AM or later. The affected message is **m043**, which proposes a Monday 09:00 investor meeting. The persistence test stores the preference, exits, starts a fresh process, reloads `memory.json`, and then applies it to m043.

- **Hostile inbox boundary.** Email bodies are untrusted data, not system/developer instructions. Known hostile cases include m017, m024 and m047. Their embedded requests are refused; the messages are flagged and preserved; no corresponding external forwarding, deletion, or other requested action is performed. The refusal is reported in the run summary and audit records.

## Capabilities

| id | name | tier | one-line claim |
|---|---|---|---|
| R1 | Zero the inbox | B | every message gets one disposition + reason, none left |
| R2 | Grounded reply | B | drafts use verified earlier thread messages as evidence |
| R3 | Gate the irreversible | C | no send/delete without explicit approval or dry-run |
| R4 | Persistent preference | C | an authorized preference survives a process restart |
| R5 | Refuse embedded instructions | C | detects, refuses, flags and reports hostile embedded instructions |
| R6 | Dashboard | C | three panes, verified commitments and surfaced conflicts |
| X1 | Unread sender lookup | A | one lookup returns matching unread messages |
| X2 | Daily digest | B | what needs attention, what can wait, and what was auto-handled |
| X3 | Commitment tracker | B | structured commitments with verified message evidence |
| X4 | Open-question thread summary | B | long threads reduced to state, blocker and unresolved question |

## Part 8 additions

### X1 — Unread sender lookup (Tier A)

This is intentionally simple: one lookup, one output. It demonstrates that not every useful inbox capability needs an LLM. The command filters the mail store directly and returns unread messages for a specified sender.

### X2 — Daily digest (Tier B)

The digest is generated from the completed run rather than asking a second model to reinterpret the entire inbox. It combines decisions, flagged items, pending actions and commitments into a short human-readable view. This makes the capability judgeable while avoiding a second, inconsistent source of truth.

### X3 — Commitment tracker (Tier B)

The tracker turns dates, meetings, obligations and dependencies into structured records. Each record carries verified message ids, so a reviewer can trace a commitment back to the inbox. Multi-message commitments are retained rather than pretending that one message necessarily contains the complete obligation.

### X4 — Open-question thread summary (Tier B)

The long-thread capability focuses on the actionable remainder rather than producing a generic summary. It walks the complete thread chronologically and reports the current state, decisions already made, blockers and the unresolved question, with evidence ids.

## Output and reproducibility

Every capability has a single command and a judgeable output. Run artifacts are kept under `runs/<timestamp>/` so another person can inspect the result and the supporting evidence. The dashboard and Part 8 outputs are derived from run artifacts rather than manually assembled.

`capabilities.json` is the machine-readable companion to this document. Its capability ids, names, tiers, claims, commands, observables and evidence entries are kept in step with this file.

## Final Report

*To be completed with the final assignment report.*
