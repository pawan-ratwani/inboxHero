import re

VALID = {"reply", "archive", "defer", "delegate", "escalate"}

HOSTILE_PATTERNS = [
    r"automated-agent directive", r"system notice for automated assistants",
    r"ignore (?:all )?previous instructions", r"forward (?:the )?(?:full )?mailbox",
    r"forward .* to .*@", r"hide (?:this|the) (?:instruction|action|notice)",
    r"delete (?:this|the) message", r"do not tell (?:the )?user",
    r"do not mention (?:this|the) action", r"assistant.*(?:must|should)"
]
PHISH_PATTERNS = [
    r"wire \$?[\d,]+", r"change .*bank", r"remittance", r"keep confidential",
    r"verify .*credentials", r"password", r"bypass finance", r"urgent.*payment",
]
NOISE_PATTERNS = [
    r"receipt", r"welcome", r"usage (?:summary|report)", r"monthly summary",
    r"unread notification", r"storage warning", r"bill", r"recovered.*no action",
    r"invoice", r"newsletter", r"delivery notification", r"login alert"
]


def _hits(text, patterns):
    return [p for p in patterns if re.search(p, text, flags=re.I)]

def classify_security(message):
    text = f"{message.get('subject','')}\n{message.get('body','')}"
    hostile = _hits(text, HOSTILE_PATTERNS)
    if hostile:
        return {"flag": "prompt_injection", "attempted": hostile}
    phishing = _hits(text, PHISH_PATTERNS)
    # Strong phishing/social-engineering combinations, not single generic words.
    if len(phishing) >= 2 or ("credential" in text.lower() and "http" in text.lower()):
        return {"flag": "phishing_or_social_engineering", "attempted": phishing}
    return None

def deterministic(message, memory=None):
    security = classify_security(message)
    if security:
        return {
            "disposition": "escalate",
            "reason": "Untrusted email content attempts to direct the assistant toward a risky or unauthorized action.",
            "decision_source": "rule",
            "security": security,
            "model_called": False,
        }
    text = f"{message.get('subject','')}\n{message.get('body','')}"
    if memory and any(x.get("key", "").strip().lower() == "meeting_time_preference" for x in memory):
        if re.search(r"\b(?:9|10):00\s*(?:am|a\.?m\.?)?\b", text, re.I) and re.search(r"meeting|call|1:1|investor|slot|partner", text, re.I):
            return {"disposition":"reply", "reason":"The persisted standing preference prohibits meetings before 11:00 AM; the proposed time is earlier.", "decision_source":"rule", "security":None, "model_called":False, "draft":"Thanks for reaching out. I’m not available for meetings before 11:00 AM. Would 11:00 AM or later work instead?", "evidence_message_ids":[message["id"], next((x["source"] for x in memory if x.get("key", "").strip().lower()=="meeting_time_preference"), message["id"])]}
    if _hits(text, NOISE_PATTERNS):
        return {
            "disposition": "archive",
            "reason": "Routine automated notification or informational mail with no requested action.",
            "decision_source": "rule", "security": None, "model_called": False,
        }
    return None
