import time, random
TASK_CODES = ["GCD","BS","INT","BFS","KNAP","DSIM"]
def new_id(task: str, seq: int, ymd: str | None=None):
    assert task in TASK_CODES
    if ymd is None: ymd = time.strftime("%Y%m%d")
    return f"{task}_{ymd}_{seq:05d}"
def rng(seed: int): return random.Random(seed)
