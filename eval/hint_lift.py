from __future__ import annotations
import numpy as np
from dataclasses import dataclass
@dataclass
class HLResult:
    levels: list[int]; pass_rate: list[float]; auc: float; deltas: list[float]; lift_total: float
def hint_lift_auc(levels: list[int], pass_rate: list[float]) -> HLResult:
    assert len(levels)==len(pass_rate) and len(levels)>=2
    x = np.array(levels, float); y = np.array(pass_rate, float)
    auc = float(np.trapz(y, x) / (x[-1]-x[0]))
    deltas = np.diff(y).tolist(); lift_total = float(y[-1]-y[0])
    return HLResult(list(levels), list(pass_rate), auc, deltas, lift_total)
if __name__=="__main__":
    lv=[0,1,2,3]; pr=[0.34,0.55,0.68,0.80]
    res = hint_lift_auc(lv, pr)
    print("HL-AUC:", round(res.auc,4))
    print("Δ:", [round(d,3) for d in res.deltas], "Total:", round(res.lift_total,3))
