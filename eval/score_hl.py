# eval/score_hl.py
import os
import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "eval"
FIG = ROOT / "fig"
EVAL.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)

CANDIDATES = [
    EVAL / "results.csv",
    EVAL / "hl_runs.csv",
]

def parse_args():
    p = argparse.ArgumentParser(description="Compute HL curve and AUC, always emit artifacts.")
    p.add_argument("--input", type=str, default=os.environ.get("ALG_HL_INPUT"),
                   help="Input CSV path. If omitted, first existing of eval/results.csv or eval/hl_runs.csv is used.")
    p.add_argument("--levels", type=str, default=os.environ.get("ALG_HL_LEVELS", "0,1,2,3"),
                   help="Comma-separated hint levels to report (default: 0,1,2,3).")
    p.add_argument("--make-dummy", action="store_true",
                   default=os.environ.get("ALG_HL_DUMMY", "0") in ("1", "true", "yes"),
                   help="Generate a dummy input when none found.")
    return p.parse_args()

def coerce_columns(df: pd.DataFrame) -> pd.DataFrame:
    # 列名ゆらぎを吸収
    cols = {c.lower(): c for c in df.columns}
    # passed
    passed_col = None
    for k in ("passed", "pass", "is_correct"):
        if k in cols:
            passed_col = cols[k]
            break
    if passed_col is None:
        raise ValueError("no 'passed'/'pass'/'is_correct' column found")

    # level
    level_col = None
    for k in ("level", "hint_level"):
        if k in cols:
            level_col = cols[k]
            break
    if level_col is None:
        raise ValueError("no 'level'/'hint_level' column found")

    out = pd.DataFrame({
        "id": df.get("id", pd.Series([None]*len(df))),
        "level": pd.to_numeric(df[level_col], errors="coerce").astype("Int64"),
        "passed": pd.to_numeric(df[passed_col], errors="coerce").clip(0, 1),
    })
    # family/difficulty があれば保持（無ければ生成/欠損）
    out["family"] = df.get("family", pd.Series(index=df.index, dtype="object"))
    # id から family 推定
    mask = out["family"].isna()
    if mask.any() and "id" in df:
        out.loc[mask, "family"] = df["id"].astype(str).str.split("_").str[0]
    if "difficulty" in df.columns:
        out["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce")
    return out.dropna(subset=["level"]).astype({"level": int, "passed": float})

def load_input(path: Path | None, make_dummy: bool) -> pd.DataFrame:
    # 入力パス解決
    if path is None:
        for c in CANDIDATES:
            if c.exists():
                path = c
                break
    if path is None:
        if make_dummy:
            # ダミーデータ（最小限）
            rng = np.random.default_rng(0)
            ids = [f"DUMMY_{i:04d}" for i in range(50)]
            rows = []
            for _id in ids:
                base = float(rng.beta(2, 5))
                p = [base]
                for _ in range(3):
                    p.append(min(1.0, p[-1] + float(rng.uniform(0.05, 0.20))))
                for lv, pp in zip([0,1,2,3], p):
                    rows.append({"id": _id, "level": lv, "passed": int(rng.random() < pp)})
            df = pd.DataFrame(rows)
            df.to_csv(EVAL / "results.csv", index=False)
            print(f"[score_hl] generated dummy: {EVAL / 'results.csv'}")
            return df
        else:
            # 入力無しでも成果物を空で作るため、空DFを返す
            print("[score_hl] no input found; proceeding with empty dataframe")
            return pd.DataFrame(columns=["id", "level", "passed"])

    df = pd.read_csv(path)
    print(f"[score_hl] loaded: {path}")
    return df

def fill_levels(df: pd.DataFrame, levels: list[int]) -> pd.DataFrame:
    # 指定levelに reindex（欠損は NaN）
    g = df.groupby("level")["passed"].mean()
    s = pd.Series(index=pd.Index(levels, name="level"), dtype=float)
    s.loc[g.index] = g.values
    return s.reset_index().sort_values("level")

def auc_from_points(levels: list[int], rates: list[float]) -> float | float:
    if len(levels) == 0:
        return float("nan")
    Lmax = max(levels)
    if Lmax <= 0 or any(pd.isna(r) for r in rates):
        return float("nan")
    x = np.array(levels, dtype=float) / float(Lmax)
    y = np.array(rates, dtype=float)
    return float(np.trapz(y, x))

def plot_curve(levels: list[int], rates: list[float], auc: float | float, title: str, path_png: Path):
    plt.figure()
    plt.plot(levels, rates, marker="o")
    plt.xlabel("Hint Level")
    plt.ylabel("Pass Rate")
    ttl = title
    if not (isinstance(auc, float) and math.isnan(auc)):
        ttl += f" (AUC={auc:.3f})"
    else:
        ttl += " (no data)"
    plt.title(ttl)
    plt.grid(True)
    plt.savefig(path_png, bbox_inches="tight")

def write_overall_artifacts(agg: pd.DataFrame, auc: float | float):
    agg.to_csv(EVAL / "hl_auc_curve.csv", index=False)
    (EVAL / "hl_auc_summary.csv").write_text(
        "level,pass_rate\n" +
        "\n".join(f"{int(r.level)},{'' if pd.isna(r.passed) else f'{float(r.passed):.6f}'}"
                  for r in agg.itertuples(index=False)) +
        f"\n\nAUC,{'' if (isinstance(auc,float) and math.isnan(auc)) else f'{auc:.6f}'}\n",
        encoding="utf-8",
    )
    (EVAL / "hl_auc.txt").write_text(
        f"HL-AUC,{'' if (isinstance(auc,float) and math.isnan(auc)) else f'{auc:.6f}'}\n",
        encoding="utf-8",
    )
    # HTML（CIのアーティファクトに含める）
    (EVAL / "eval_report.html").write_text(
        """<!doctype html><meta charset="utf-8">
<title>HL-AUC report</title>
<h1>Hint-Lift (HL) Report</h1>
<p>AUC: """ +
        ("N/A" if (isinstance(auc, float) and math.isnan(auc)) else f"{auc:.6f}") +
        """</p>
<p><img src="../fig/hl_auc.png" alt="HL curve" style="max-width:100%"></p>
""",
        encoding="utf-8",
    )

def write_group_curves(df: pd.DataFrame, levels: list[int]):
    def _curve(g):
        agg = fill_levels(g, levels)
        auc = auc_from_points(list(agg["level"]), list(agg["passed"]))
        return agg, auc

    # family
    fam_col = "family" if "family" in df.columns else None
    if fam_col is None and "id" in df.columns:
        fam_col = "family"
        df = df.copy()
        df[fam_col] = df["id"].astype(str).str.split("_").str[0]

    if fam_col:
        for fam, g in df.groupby(fam_col):
            agg, auc = _curve(g)
            agg.to_csv(EVAL / f"hl_auc_curve_{fam}.csv", index=False)
            plot_curve(list(agg["level"]), list(agg["passed"]), auc, f"{fam}", FIG / f"hl_auc_{fam}.png")

    if "difficulty" in df.columns:
        for d, g in df.groupby("difficulty"):
            agg, auc = _curve(g)
            agg.to_csv(EVAL / f"hl_auc_curve_diff{d}.csv", index=False)
            plot_curve(list(agg["level"]), list(agg["passed"]), auc, f"Difficulty {d}", FIG / f"hl_auc_diff{d}.png")

def main():
    args = parse_args()
    # levels
    levels = [int(x) for x in str(args.levels).split(",") if str(x).strip() != ""]

    raw = load_input(Path(args.input) if args.input else None, make_dummy=args.make_dummy)
    if raw.empty:
        # 全成果物を空テンプレで出す
        agg = pd.DataFrame({"level": levels, "passed": [float("nan")] * len(levels)})
        auc = float("nan")
    else:
        df = coerce_columns(raw)
        agg = fill_levels(df, levels)
        auc = auc_from_points(list(agg["level"]), list(agg["passed"]))

    # 図（全体）
    plot_curve(list(agg["level"]), list(agg["passed"]), auc, "HL curve", FIG / "hl_auc.png")
    # CSV/TXT/HTML
    write_overall_artifacts(agg, auc)
    # 追加のファミリ/難易度別（存在する場合のみ）
    if not raw.empty:
        write_group_curves(df, levels)

    print(f"[score_hl] AUC = {('N/A' if (isinstance(auc,float) and math.isnan(auc)) else f'{auc:.6f}')} ")
    print("[score_hl] Saved: fig/hl_auc.png, eval/hl_auc_curve.csv, eval/hl_auc_summary.csv, eval/hl_auc.txt, eval/eval_report.html")

if __name__ == "__main__":
    main()
