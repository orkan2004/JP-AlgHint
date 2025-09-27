import json, os, sys, hashlib, subprocess, shutil, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

def sha1(xs): return hashlib.sha1(",".join(map(str, xs)).encode()).hexdigest()

def run_case(item):
    tmp = ROOT / "data" / "_tmp_unit"
    os.makedirs(tmp, exist_ok=True)
    p = tmp / "one.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(item, f, ensure_ascii=False)
    try:
        r = subprocess.run([sys.executable, "eval/verify_witness.py"],
                           cwd=ROOT, text=True, capture_output=True)
        assert r.returncode == 0
        return r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def test_bfs_ok():
    parent = [-1, 0, 1]  # 0-1-2, src=0, target=2 → dist=2
    item = {
        "id": "BFS_20250927_00001",
        "io_spec": {"input": {"n": 3, "edges": [[0,1],[1,2]], "src": 0, "target": 2}},
        "witness": {"parent_hash": sha1(parent), "shortest_len": 2},
    }
    out = run_case(item)
    assert "BFS witness ok" in out

def test_int_ok():
    chosen = [(1,3),(3,5)]
    item = {
        "id": "INT_20250927_00002",
        "io_spec": {"input": {"intervals": [(1,3),(2,4),(3,5)]}},
        "witness": {"chosen_intervals": chosen},
    }
    out = run_case(item)
    assert "INT" in out and "ok" in out.lower()
