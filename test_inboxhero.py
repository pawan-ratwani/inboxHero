import json, tempfile
from pathlib import Path
from inboxhero.core import load_inbox, validate_inbox
from inboxhero.memory import remember, recall_all
from inboxhero.rules import deterministic

ROOT=Path(__file__).parent

def test_fixture_shape():
    msgs=load_inbox(ROOT/'inbox.json')
    assert len(msgs)==100
    assert len(validate_inbox(msgs))==100

def test_hostile_messages_are_flagged_by_rule():
    msgs=load_inbox(ROOT/'inbox.json')
    by={m['id']:m for m in msgs}
    for mid in ('m017','m024','m047'):
        d=deterministic(by[mid], [])
        assert d and d['disposition']=='escalate'
        assert d['security']['flag']=='prompt_injection'
        assert d['model_called'] is False

def test_persistent_preference_survives_reload():
    with tempfile.TemporaryDirectory() as td:
        import inboxhero.memory as mem
        old=mem.MEMORY_FILE
        mem.MEMORY_FILE=Path(td)/'memory.json'
        try:
            remember('meeting_time_preference','Do not schedule meetings before 11:00 AM.','m041')
            assert mem.recall_all()[0]['source']=='m041'
            # Fresh read from disk, not a process-global list.
            assert json.loads((Path(td)/'memory.json').read_text())[0]['key']=='meeting_time_preference'
        finally:
            mem.MEMORY_FILE=old
