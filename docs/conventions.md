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
## 9/20 追記: タグ定義（固定語彙）
- 分野: number / search / greedy / graph / dp / ds
- 技能: math / proof / simulation / boundary / invariant
- 難易度: beginner / intermediate / advanced

## 9/20 追記: 誤答コード（拡充）
- LOWER_UPPER_SWAP: 範囲端の入れ替えミス
- NOT_SORTED_INPUT: 入力昇順の前提を満たさない
- TIE_BREAK_WRONG: タイブレーク規則の誤り
- OVERFLOW_EDGE_IGNORED: 端でのオーバーフロー想定なし
- INDEX_BASE_MISMATCH: 0始まり/1始まりの取り違え
- END_EXCLUSIVE_CONFUSION: 半開/閉区間の取り違え
