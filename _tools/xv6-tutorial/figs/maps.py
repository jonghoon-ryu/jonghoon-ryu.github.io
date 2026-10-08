from figs.common import changemap
PREV = {"v0.1-x86_64-c": "06aad25", "v0.2-x86_64-c": "v0.1-x86_64-c", "step-01": "v0.2-x86_64-c"}
for i in range(2, 11):
    PREV[f"step-{i:02d}"] = f"step-{i - 1:02d}"
def _mk(tag):
    return lambda: changemap(PREV[tag], tag)
for _t in PREV:
    globals()["map_" + _t.replace("-", "_").replace(".", "_")] = _mk(_t)
