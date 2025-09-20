import csv, argparse, statistics as st
def read_rates(csv_path):
    lv_cols = ["pass_lv0","pass_lv1","pass_lv2","pass_lv3"]
    rows = []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append([float(row[c]) for c in lv_cols])
    if not rows: return [0,0,0,0]
    return [st.mean(col) for col in zip(*rows)]
def auc_from_levels(r):
    return sum((r[i]+r[i+1])/2 for i in range(3)) / 3.0
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rates = read_rates(a.csv); auc = auc_from_levels(rates)
    out = "Hint-Lift summary\n" + \
          f"rates lv0..lv3: {', '.join(f'{x:.3f}' for x in rates)}\n" + \
          f"HL-AUC (normalized 0..1): {auc:.4f}\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f: f.write(out)
    else:
        print(out, end="")
