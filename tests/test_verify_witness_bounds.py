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

# --- RSQ: 範囲外（負・n超）や L>R は 0 になる ---
@pytest.mark.parametrize(
    "queries,answers",
    [
        ([[-3, -1]], [0]),                        # 左に外れる
        ([[5, 9]],   [0]),                        # 右に外れる（n=4）
        ([[2, 1]],   [0]),                        # 逆順（L>R）→0
        ([[-3, -1], [5, 9], [2, 1]], [0, 0, 0]),  # まとめて
    ],
)
def test_rsq_out_of_bounds_zero(queries, answers):
    item = {
        "id": "RSQ_20251001_00001",  # 末尾は5桁
        "io_spec": {"input": {"arr": [1, 2, 3, 4], "queries": queries}},
        "witness": {"answers": answers},
    }
    out = run_case(item)
    assert_all_pass(out)

# --- UF: 1-based 入力でも通る ---
@pytest.mark.parametrize(
    "unions,queries,answers",
    [
        (
            [[1, 2], [2, 3]],                        # 1-based unions
            [["connected", 1, 3], ["connected", 1, 4]],
            [1, 0],                                  # 実装が 1/0 を期待する想定
        ),
        (
            [[1, 1]],
            [["connected", 1, 1]],
            [1],
        ),
    ],
)
def test_uf_one_based_ok(unions, queries, answers):
    item = {
        "id": "UF_20251001_00001",
        "io_spec": {"input": {"n": 4, "unions": unions, "queries": queries}},
        "witness": {"answers": answers},
    }
    out = run_case(item)
    assert_all_pass(out)
