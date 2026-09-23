import argparse, json
from datetime import datetime
from pathlib import Path
from inboxhero.core import run
from inboxhero.dashboard import render

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--inbox",default="inbox.json")
    ap.add_argument("--model",default="qwen3.5")
    ap.add_argument("--run-dir",default=None)
    ap.add_argument("--execute",action="store_true",help="Interactively approve irreversible actions")
    ap.add_argument("--learn-preferences-only",action="store_true",help="Persist owner preferences and exit; used for restart demonstration")
    args=ap.parse_args()
    stamp=datetime.now().strftime("%Y%m%dT%H%M%S")
    run_dir=Path(args.run_dir or Path("runs")/stamp)
    data=run(args.inbox,run_dir,args.model,dry_run=not args.execute,learn_preferences=args.learn_preferences_only)
    # Dashboard is generated from run.json data, never hand assembled.
    if args.learn_preferences_only:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    render(data,run_dir/"dashboard.html")
    print(json.dumps(data["summary"],indent=2))
    if args.execute:
        audit=[]
        outbox=Path("outbox"); outbox.mkdir(exist_ok=True)
        for item in data["pending_actions"]:
            print("\nIRREVERSIBLE ACTION")
            print(json.dumps(item,indent=2,ensure_ascii=False))
            answer=input("Approve this action? [yes/no]: ").strip().lower()
            entry={"message_id":item["message_id"],"action":item["proposed_action"],"proposed":item,
                   "human_decision":answer,"result":"not_sent"}
            if answer == "yes" and item["proposed_action"] == "send":
                payload={"message_id":item["message_id"],"body":item.get("draft") or ""}
                (outbox/f"{item['message_id']}.json").write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding="utf-8")
                entry["result"]="written_to_outbox"
            audit.append(entry)
        (run_dir/"audit.jsonl").write_text("\n".join(json.dumps(x) for x in audit),encoding="utf-8")
        print(f"Audit written to {run_dir/'audit.jsonl'}")

if __name__ == "__main__": main()
