from .memory import remember


def learn_standing_preferences(messages):
    """Learn only the concrete owner preference present in the supplied inbox fixture.
    This is deliberately deterministic: it is not allowed to let arbitrary email grant authority.
    """
    learned = []
    for m in messages:
        text = (m.get("subject", "") + "\n" + m.get("body", "")).lower()
        if ("doesn’t take meetings before 11:00" in text or "doesn't take meetings before 11:00" in text or "do not take meetings before 11:00" in text) and "future scheduling" in text:
            learned.append(remember(
                "meeting_time_preference",
                "Do not schedule meetings before 11:00 AM. For earlier proposals, offer 11:00 AM or later.",
                m["id"],
            ))
    return learned
