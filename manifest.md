# inboxHero Manifest

## Scope
- Local-only mock inbox agent.
- Input: `inbox.json`.
- Output sends: `outbox/`, one file per approved message.
- No real email account, SMTP, webhook, or external delivery.
- Model: local Ollama `qwen3.5` for context-dependent classification/drafting only.
- Framework: none. The project uses Python standard-library components to keep routing, safety gates, persistence, and audit behavior explicit and testable.

## Inbox assumptions
- Input is a JSON array of message objects with `id`, `thread_id`, `from`, `to`, `subject`, `timestamp`, `body`, `unread`.
- `id` uniquely identifies a message.
- `thread_id` identifies a conversation.
- `timestamp` is ISO-8601.
- `unread` is boolean.
- Email content is untrusted data, not system/developer instructions.

## Dispositions
Every message receives exactly one:
- `reply`: a response is appropriate.
- `archive`: no response/action is needed.
- `defer`: action should happen later or after a condition.
- `delegate`: work should be handed to another person/team.
- `escalate`: human attention is required due to ambiguity, risk, authority, security, legal/financial consequence, or another safety boundary.

## Zeroing invariant
A completed run is valid only when the number of decisions equals the number of input messages, every input ID appears exactly once, every disposition is valid, and every decision has a non-empty reason.

## Routing
High-confidence obvious cases are resolved by deterministic rules before any model call. Context-dependent cases are sent to local Ollama `qwen3.5`. The run records `decision_source` and `model_called`; the summary reports how many messages never required a model call.

## Context retrieval
Retrieval method: `thread_walk`. For context-dependent work, all messages in the same `thread_id` are retrieved from the mail store and ordered chronologically. Evidence IDs in drafts/commitments are verified against the mail store and the retrieved context. If required information is absent from the inbox, the system says so and drafts nothing.

## Action safety
Reversible: `draft_reply`, `archive`, `defer`, `delegate`, `escalate`.
Irreversible: `send`, `delete`.
- `send` is irreversible because an outgoing message cannot be unsent in this simulation.
- `delete` is irreversible because this design has no trash/recovery mechanism.
- The system does not automatically delete hostile/phishing messages; they remain in the inbox and are flagged.
- Every irreversible action requires explicit human approval. Dry-run mode is also supported and is the default.
- Approval is per irreversible action, not per every classification, to avoid approval fatigue while preserving control over external consequences.

## Sending
An approved send writes exactly one message to `outbox/`. No other delivery mechanism exists.

## Audit
Every gated irreversible action records the proposed action, human decision, and result in the run audit log.

## Standing instructions
Persistent preferences are stored in `memory.json` and survive process exit/restart. Each preference records its source message ID. Preference updates require an authorized owner instruction; email cannot grant itself authority to alter safety rules.

Demonstrated preference: `m041` states that Sam does not take meetings before 11:00 AM and earlier proposals should offer 11:00 AM or later. Affected message: `m043`, which proposes a Monday 09:00 investor meeting. The restart demonstration stores the preference, exits, restarts, reloads `memory.json`, and applies it to `m043`.

## Hostile inbox
Assistant-directed instructions inside email are untrusted. Detected hostile instructions are refused, assigned disposition `escalate`, flagged, preserved, and cause no outbox write or other action on their behalf. The run summary names the message IDs and attempted actions.
Known test cases in the supplied inbox include `m017`, `m024`, and `m047`.

## Dashboard
A completed run produces `dashboard.html` from run JSON artifacts. Exactly three panes are rendered:
1. Pending actions — irreversible actions awaiting human approval, with message, action, and why human approval is required.
2. Flagged — refused actions including hostile messages, phishing, and ungrounded requests, with attempted action and system response.
3. Commitments — dates/deadlines/obligations rendered as a calendar. Every commitment has verified source message IDs. At least one multi-message commitment is expected when supported by the inbox. Conflicts at the same time are explicitly surfaced.
