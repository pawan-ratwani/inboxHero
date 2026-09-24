# inboxHero

A local, safety-gated agentic mock-inbox processor for the assignment Parts 1–9.

## Run

From this directory:

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

Run the whole capability set:

```bash
python main.py --all
```

The default `python main.py` runs a completed inbox pass and produces the dashboard and Part 8 artifacts.

## Model configuration

The model provider is **not hardcoded in the application**. Runtime model settings are loaded by `config.py` from environment variables, with an optional local `.env` file. Environment variables take precedence.

Default configuration preserves the assignment target:

```text
INBOXHERO_MODEL_PROVIDER=ollama
INBOXHERO_MODEL_NAME=qwen3.5
INBOXHERO_MODEL_BASE_URL=http://127.0.0.1:11434
INBOXHERO_MODEL_API_KEY=
INBOXHERO_MODEL_TIMEOUT=30
```

For Ollama:

```bash
ollama serve
ollama pull qwen3.5
```

The model client currently supports `ollama` and `openai-compatible` providers. For an OpenAI-compatible endpoint, set for example:

```text
INBOXHERO_MODEL_PROVIDER=openai-compatible
INBOXHERO_MODEL_NAME=<model-name>
INBOXHERO_MODEL_BASE_URL=https://<provider-host>
INBOXHERO_MODEL_API_KEY=<api-key>
```

No real email account, SMTP service, webhook, or external delivery is used. If the configured model provider is unavailable or fails, the application fails safe for context-dependent decisions by escalating rather than inventing a result.

## Capabilities

- **R1 — Zero the inbox (B):** one disposition and reason for every message.
- **R2 — Grounded reply (B):** thread-walk retrieval and verified evidence ids.
- **R3 — Gate the irreversible (C):** send/delete behind per-action approval or dry-run.
- **R4 — Persistent preference (C):** preference survives a complete process restart.
- **R5 — Refuse embedded instructions (C):** hostile instructions are refused, flagged and preserved.
- **R6 — Dashboard (C):** exactly three panes: pending actions, flagged, commitments.
- **X1 — Unread sender lookup (A):** one deterministic lookup, no model call.
- **X2 — Daily digest (B):** needs you, can wait, and auto-handled sections.
- **X3 — Commitment tracker (B):** structured deadlines/meetings/obligations with evidence.
- **X4 — Open-question thread summary (B):** long-thread state, blocker and unresolved question.

## Outputs

Each completed run creates `runs/<timestamp>/` containing `run.json` and `audit.jsonl`; applicable capabilities additionally create `dashboard.html`, `daily_digest.md`, `commitments.json`, `commitments.md`, and `thread_summaries/<thread>.md`.

Approved sends write exactly one JSON file per message under `outbox/`. Dry-run never writes an outbox message.

## Safety

Email content is untrusted. Embedded assistant-directed instructions cannot change system permissions or standing preferences. Hostile/phishing messages are flagged and preserved. Legal, financial, ambiguous, security-sensitive and user-time commitments are escalated. Irreversible actions require explicit human approval.

## Tier coverage

Tier A: X1.  Tier B: R1, R2, X2, X3, X4.  Tier C: R3, R4, R5, R6.
