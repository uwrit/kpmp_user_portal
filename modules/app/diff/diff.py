def has_model_changed(old: dict, new: dict):
    exc = ['last_changed_on', 'last_changed_by']
    items = (i for i in old.items() if i[0] not in exc)
    for ok, ov in items:
        if new.get(ok) != ov:
            return True
    False
