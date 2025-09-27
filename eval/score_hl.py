# eval/score_hl.py
import os, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RESULTS = "eval/results.csv"
os.makedirs("fig", exist_ok=True)
os.makedirs("eval", exist_ok=True)

def maybe_make_dummy():
    if os.path.exists(RESULTS): return
    # ダミーの評価結果を生成（動作確認用）
    np.random.seed(0)
    ids=[f"DUMMY_{i:04d}" for i in range(200)]
    levels=[0,1,2,3]
    rows=[]
    for _id in ids:
        base=np.random.beta(2,5)
        p=[base]
        for _ in range(3):
            p.append(min(1.0, p[-1]+np.random.uniform(0.05,0.20)))
        for lv,pp in zip(levels,p):
            rows.append({"id":_id,"level":lv,"passed":int(np.random.rand()<pp)})
    pd.DataFrame(rows).to_csv(RESULTS, index=False)
    print("generated dummy:", RESULTS)

def hl_curve_and_auc(df: pd.DataFrame):
    # levelごとの通過率
    agg = df.groupby("level")["passed"].mean().reset_index().sort_values("level")
    xs = agg["level"].to_numpy(dtype=float)
    ys = agg["passed"].to_numpy(dtype=float)
    if xs.max() == 0:
        auc = float(ys.mean())
    else:
        x_norm = xs / xs.max()
        auc = float(np.trapz(ys, x_norm))
    return agg, auc

def main():
    maybe_make_dummy()
    df = pd.read_csv(RESULTS)
    agg, auc = hl_curve_and_auc(df)
    agg.to_csv("eval/hl_auc_curve.csv", index=False)
    with open("eval/hl_auc.txt","w",encoding="utf-8") as f:
        f.write(f"HL-AUC,{auc:.6f}\n")
    # 図の保存
    plt.figure()
    plt.plot(agg["level"], agg["passed"], marker="o")
    plt.xlabel("Hint Level")
    plt.ylabel("Pass Rate")
    plt.title(f"HL Curve (AUC={auc:.3f})")
    plt.grid(True)
    plt.savefig("fig/hl_auc.png", bbox_inches="tight")
    print(f"HL-AUC: {auc:.6f}")
    print("Saved: eval/hl_auc_curve.csv, eval/hl_auc.txt, fig/hl_auc.png")

if __name__ == "__main__":
    main()
