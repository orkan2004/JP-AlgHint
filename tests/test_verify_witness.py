import json, os, sys, hashlib, subprocess, shutil, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

def sha1(xs):
    return hashlib.sha1(",".join(map(str, xs)).encode()).hexdigest()

def run_case(item):
    # data/_tmp_unit に1件だけ投入して検証を走らせる
    tmp = ROOT / "data" / "_tmp_unit"
    os.makedirs(tmp, exist_ok=True)
    with open(tmp / "one.json", "w", encoding="utf-8") as f:
        json.dump(item, f, ensure_ascii=False)
    try:
        r = subprocess.run([sys.executable, "eval/verify_witness.py"],
                           cwd=ROOT, text=True, capture_output=True)
        assert r.returncode == 0, r.stdout + r.stderr
        return r.stdout + r.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def assert_all_pass(out: str):
    m = re.search(r"Witness check:\s*(\d+)\s*/\s*(\d+)", out)
    assert m, f"summary not found in output:\n{out}"
    passed, total = map(int, m.groups())
    assert passed == total, f"witness failures exist: {passed}/{total}\n{out}"

def test_rsq_ok():
    item = {
        "id": "RSQ_20250928_00001",
        "io_spec": {"input": {"arr": [1, 2, 3, 4], "queries": [[0, 1], [1, 3]]}},
        "witness": {"answers": [3, 9]},  # 0-based: [1+2, 2+3+4]
    }
    out = run_case(item)
    # verify_witness.py は要約のみ標準出力に出す設計なので、summaryで合格を確認
    assert_all_pass(out)

def test_witness_smoke():
    # 0-1-2 の鎖, src=0, target=2 → dist=2
    parent = [-1, 0, 1]
    item = {
        "id": "BFS_20250927_00001",
        "io_spec": {"input": {"n": 3, "edges": [[0,1],[1,2]], "src": 0, "target": 2}},
        "witness": {"parent_hash": sha1(parent), "shortest_len": 2},
    }
    out = run_case(item)
    assert_all_pass(out)
