import json, os, sys, hashlib, subprocess, shutil, re, pathlib, pytest

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
    assert_all_pass(out)

def test_uf_ok():
    # 0-1-2 を union、(0,2) は連結、(0,3) は非連結
    item = {
        "id": "UF_20250928_00001",
        "io_spec": {
            "input": {
                "n": 4,
                "ops": [
                    ["union", 0, 1],
                    ["union", 1, 2],
                    ["connected", 0, 2],
                    ["connected", 0, 3],
                ],
            }
        },
        # answersの表記（1/0 or "yes"/"no"）は検証器側に合わせてOK。
        # ここでは 1/0 を想定。違う場合でも最後は summary 判定に集約。
        "witness": {"answers": [1, 0]},
    }
    out = run_case(item)
    assert_all_pass(out)

def test_witness_smoke():
    # 0-1-2 の鎖, src=0, target=2 → dist=2
    parent = [-1, 0, 1]
    item = {
        "id": "BFS_20250927_00001",
        "io_spec": {"input": {"n": 3, "edges": [[0, 1], [1, 2]], "src": 0, "target": 2}},
        "witness": {"parent_hash": sha1(parent), "shortest_len": 2},
    }
    out = run_case(item)
    assert_all_pass(out)

# RSQ: 範囲外（負やn超過）や L>R は 0 になる
@pytest.mark.parametrize(
    "queries,answers",
    [
        ([[-3, -1]], [0]),                        # 左に外れる
        ([[5, 9]],   [0]),                        # 右に外れる（n=4）
        ([[2, 1]],   [0]),                        # 逆順（L>R）→0
        ([[-3, -1], [5, 9], [2, 1]], [0, 0, 0]), # まとめて
    ],
)
def test_rsq_out_of_bounds_zero(queries, answers):
    item = {
        "id": "RSQ_20251001_00001",
        "io_spec": {"input": {"arr": [1, 2, 3, 4], "queries": queries}},
        "witness": {"answers": answers},
    }
    out = run_case(item)
    assert_all_pass(out)

# UF: 1-based 入力でも通る（検証器が0/1-basedを自動吸収）
@pytest.mark.parametrize(
    "ops,answers",
    [
        (
            [["union", 1, 2], ["union", 2, 3], ["connected", 1, 3], ["connected", 1, 4]],
            [1, 0],  # 1-2-3 連結 → (1,3)=連結, (1,4)=非連結
        ),
        (
            [["union", 1, 1], ["connected", 1, 1]],
            [1],     # 自己連結は True
        ),
    ],
)
def test_uf_one_based_ok(ops, answers):
    item = {
        "id": "UF_20251001_00001",
        "io_spec": {"input": {"n": 4, "ops": ops}},
        "witness": {"answers": answers},
    }
    out = run_case(item)
    assert_all_pass(out)
