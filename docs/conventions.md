# IDs
ID = {TASK}_{YYYYMMDD}_{5桁連番}
TASK ∈ {GCD, BS, INT, BFS, KNAP, DSIM}  # 数論/二分/区間/BFS/ナップ/データ構造シミュ

# タグ
分野: number, search, greedy, graph, dp, ds
技能: math, invariant, proof, simulation, boundary
難易度: beginner, intermediate, advanced

# 誤答コード（distractors.code）
OFF_BY_ONE, MID_OVERFLOW, WRONG_GREEDY_ORDER, MOD_NEGATIVE, TAKE_MAX_VALUE_ONLY, UNDERFLOW_IGNORED

# witness（機械可検証の証拠）例
BFS: {shortest_len, parent_hash}
INT: {chosen_intervals}
KNAP: {opt_value, chosen_items}
