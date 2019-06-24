import uwgs
from modules.app import app
from typing import *

_client = uwgs.Client(app.config['UWGS_CERT'], app.config['UWGS_KEY'], app.config['UWGS_URL'])

def get_for_one(id: str, group_ids: Iterable[str]) -> Iterable[str]:
    payloads = _client.get_effective_memberships(group_ids)
    return _extract_groups(id, group_ids, payloads)

def get_for_many(ids: Iterable[str], group_ids: Iterable[str]) -> Dict[str, Iterable[str]]:
    payloads = _client.get_effective_memberships(group_ids)
    grps = {}
    for id in ids:
        grps[id] = _extract_groups(id, group_ids, payloads)
    return grps


def _extract_groups(id: str, group_ids: Iterable[str], payloads: Iterable[uwgs.Payload]) -> Iterable[str]:
    ty = 'eppn'
    if id.endswith('@washington.edu'):
        id = id.split('@')[0]
        ty = 'uwnetid'
    grps = []
    for p in payloads:
        if not p.ok:
            continue
        dat = p.data
        members = dat['data']
        meta = dat['meta']
        if id in (u['id'] for u in members if u['type'] == ty):
            grps.append(meta['id'])
    return grps