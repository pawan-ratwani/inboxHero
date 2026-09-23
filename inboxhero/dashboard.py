import html, json
from pathlib import Path

def render(data, output):
    def esc(x): return html.escape(str(x if x is not None else ""))
    p = []
    p.append("<!doctype html><html><head><meta charset='utf-8'><title>inboxHero Dashboard</title><style>body{font-family:system-ui;margin:0;background:#f5f5f5;color:#222}main{max-width:1200px;margin:auto}.pane{background:white;margin:18px 0;padding:18px;border:1px solid #ddd;border-radius:10px}table{width:100%;border-collapse:collapse}th,td{padding:9px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}.flag{border-left:5px solid #b33}.conflict{border-left:5px solid #c80}.cal{display:grid;gap:10px}.event{padding:12px;border:1px solid #ddd;border-radius:8px}.meta{font-size:.9em;color:#666}code{background:#eee;padding:2px 4px}</style></head><body><main>")
    p.append("<h1>inboxHero — completed run</h1>")
    p.append("<section class='pane'><h2>1. Pending actions</h2><table><tr><th>Message</th><th>Proposed action</th><th>Why human</th></tr>")
    for x in data["pending_actions"]:
        p.append(f"<tr><td><code>{esc(x['message_id'])}</code></td><td>{esc(x['proposed_action'])}<br><small>{esc(x.get('draft'))}</small></td><td>{esc(x['reason_human_required'])}</td></tr>")
    if not data["pending_actions"]: p.append("<tr><td colspan='3'>None.</td></tr>")
    p.append("</table></section>")
    p.append("<section class='pane'><h2>2. Flagged</h2><table><tr><th>Message</th><th>What was attempted</th><th>What the system did instead</th></tr>")
    for x in data["flagged"]:
        attempted = "; ".join(map(str,x.get("attempted",[])))
        p.append(f"<tr class='flag'><td><code>{esc(x['message_id'])}</code></td><td>{esc(attempted)}</td><td>{esc(x['system_did'])}<br>Preserved: {esc(x['preserved'])}</td></tr>")
    if not data["flagged"]: p.append("<tr><td colspan='3'>None.</td></tr>")
    p.append("</table></section>")
    p.append("<section class='pane'><h2>3. Commitments</h2>")
    if data["conflicts"]:
        p.append("<h3>Conflicts</h3>")
        for c in data["conflicts"]:
            p.append(f"<div class='event conflict'><b>CONFLICT — {esc(c['date'])} {esc(c['time'])}</b><br>{esc(' vs '.join(c['commitment_titles']))}<br><span class='meta'>Evidence: {esc(', '.join(c['evidence_message_ids']))}</span></div>")
    p.append("<div class='cal'>")
    for c in sorted(data["commitments"], key=lambda x:(x.get('date') or '9999',x.get('time') or '99:99')):
        p.append(f"<div class='event'><b>{esc(c.get('date'))} {esc(c.get('time'))}</b> — {esc(c.get('title'))}<br>{esc(c.get('obligation'))}<br><span class='meta'>Evidence: {esc(', '.join(c.get('evidence_message_ids',[])))}</span></div>")
    if not data["commitments"]: p.append("<div>None extracted.</div>")
    p.append("</div></section></main></body></html>")
    Path(output).write_text("".join(p),encoding="utf-8")
