# JP-AlgHint

- JSON スキーマ: docs/schema.json, eval/schema.json
- バリデーション: python eval/validate_all.py
- ID パターン: ^(GCD|BS|INT|BFS|KNAP|DSIM|MST|RSQ|UF)_\d{8}_\d{5}$

## 開発フロー
1. ブランチ作成: git switch -c feature/<topic>
2. 変更 → コミット → git push -u origin feature/<topic>
3. GitHub で PR を作成（CI が通ったらレビュー＆マージ）

[![CI](https://github.com/orkan2004/JP-AlgHint/actions/workflows/ci.yml/badge.svg)](https://github.com/orkan2004/JP-AlgHint/actions/workflows/ci.yml)

### Setup
```bash
python -m pip install -r requirements.txt
python eval/check_schema_sync.py
python eval/validate_all.py


## Setup

```powershell
python -m pip install -r requirements.txt

Witness 仕様 早見表（BFS / INT / RSQ / UF / MST）

本リポジトリの eval/verify_witness.py は、各ファミリ（問題種別）の witness を再計算して妥当性を検証します。
CI では eval/witness_report.txt に各ケースの結果を出力し、標準出力にサマリ（Witness check: P/T）を表示します。

共通：入力は基本的に io_spec.input を参照します（一部、互換のため instance.params も読みます）

family は id のプレフィックス（例：BFS_20250928_000001 → BFS）で判定

失敗時は False と理由（例：answers mismatch）を出力

一覧（ざっくり）
Family	期待する witness	主な検証内容	インデックス
BFS	parent_hash（親配列の SHA1）、shortest_len（整数）	src からの BFS で親配列が正しい / target があれば最短距離が一致	0-based
INT（区間スケジューリング）	chosen_intervals（区間集合）	互いに非交差である / 貪欲最適数と同数（最適性チェック）	0-based（開始・終了は整数）
RSQ（区間和）	answers（各クエリの和）	前計算の prefix-sum で再計算した和と一致	0/1 どちらも可（自動判別）
UF（Disjoint Set / Union-Find）	answers（各 connected クエリの答え）	union と connected を逐次適用し、連結判定の列が一致	0-based（※将来 1-based も検討）
MST（最小全域木 / Kruskal）	weight（または total_weight）、edges_hash	Kruskal で得た MST の総重み・辺集合ハッシュと一致	0-based

ℹ️ ハッシュの仕様（実装互換）

parent_hash：親配列 parent をカンマ連結して SHA1（例：-1,0,1,1,3,...）

edges_hash：無向辺を (min(u,v), max(u,v)) に正規化しソート、u-v 文字列を改行で連結して SHA1
（実装に合わせた“正規化+ソート+連結→SHA1”です。生成側で具体実装が必要なら下のヘルパ例を参照）

各ファミリの詳細
BFS（最短路・親配列）

入力例

{
  "id": "BFS_20250927_000001",
  "io_spec": { "input": { "n": 5, "edges": [[0,1],[1,2],[1,3],[3,4]], "src": 0, "target": 4 } },
  "witness": {
    "parent_hash": "e2d0...f9c",   // 親配列 [-1,0,1,1,3] の SHA1
    "shortest_len": 3                // src=0 → target=4 の最短距離
  }
}


検証
src から BFS を再実行し、

親配列が木として整合（根は -1、その他は隣接）

target があれば dist[src→target] == shortest_len
を確認します。

親配列ハッシュ生成（ヘルパ）

import hashlib
def sha1_parent(parent):
    s = ",".join(map(str, parent))      # 例: "-1,0,1,1,3"
    return hashlib.sha1(s.encode()).hexdigest()

INT（区間スケジューリング：最大本数）

入力例

{
  "id": "INT_20250927_000002",
  "io_spec": { "input": { "intervals": [[1,3], [2,4], [3,5]] } },
  "witness": {
    "chosen_intervals": [[1,3], [3,5]]
  }
}


検証

chosen_intervals が 互いに交差しない（[l1,r1] と [l2,r2] が重ならない）

終端でソートした 貪欲アルゴリズム の解の本数と 同数（最適性）
を確認します。

注：区間の境界は整数、原則 0-based。閉区間/半開区間の取り扱いは実装に合わせて“接点で非交差”になるよう定義（[1,3] と [3,5] は非交差として扱います）。

RSQ（Range Sum Query：区間和）

入力例（柔軟に解釈）

{
  "id": "RSQ_20250928_000003",
  "io_spec": {
    "input": {
      "arr": [2, -1, 3, 4],
      "queries": [[0,2], [2,3]]
    }
  },
  "witness": {
    "answers": [4, 7]
  }
}


キーの互換

配列は arr / array / a、クエリは queries / qs を受理

さらに後方互換として instance.params からも読む実装です

検証

prefix-sum で各クエリ [l,r] の和を再計算

0-based / 1-based を自動判別

0-based と 1-based の両方で計算し、どちらか一致すれば OK

入力が見つからない場合は 形式のみの緩い検証（answers がリストなら OK）になります。

UF（Disjoint Set / Union-Find）

入力例

{
  "id": "UF_20250928_000001",
  "io_spec": {
    "input": {
      "n": 4,
      "ops": [
        ["union", 0, 1],
        ["union", 1, 2],
        ["connected", 0, 2],
        ["connected", 0, 3]
      ]
    }
  },
  "witness": { "answers": [1, 0] }     // connected の問合せに対応（順序どおり）
}


検証

ops を先頭から順に適用

"union", u, v：併合

"connected", u, v：連結なら 1 / 非連結なら 0（true/false 互換も可）

witness.answers が connected クエリの出現順 に一致すること

インデックスは 0-based 前提（n は要素数）。将来的に 1-based も寛容化予定です。

MST（最小全域木：Kruskal）

入力例

{
  "id": "MST_20250928_000007",
  "io_spec": {
    "input": {
      "n": 5,
      "edges": [
        [0,1,4], [1,2,2], [1,3,5], [2,3,1], [3,4,3]
      ]               // [u, v, w]（無向、0-based）
    }
  },
  "witness": {
    "weight": 10,     // または total_weight
    "edges_hash": "a3c1...b7e"
  }
}


検証

Kruskal（辺重み昇順 + DSU）で MST を再計算

総重み（weight or total_weight）と 辺集合ハッシュ（edges_hash）の両方が一致

辺ハッシュ生成（ヘルパ）

import hashlib

def mst_edges_hash(edges):  # edges: 選ばれた辺 [(u,v,w), ...]
    norm = []
    for u, v, _ in edges:
        a, b = (u, v) if u <= v else (v, u)  # 無向を正規化
        norm.append((a, b))
    norm.sort()
    s = "\n".join(f"{a}-{b}" for a, b in norm)
    return hashlib.sha1(s.encode()).hexdigest()

実行方法（ローカル）
python eval/verify_witness.py
# => eval/witness_report.txt を生成
#    標準出力: "Witness check: {passed}/{total}"

よくある落とし穴

BFS：parent の根は必ず -1。親が隣接になっていないと失敗します

INT：[l,r] が“接している”場合は非交差とみなします（[1,3] と [3,5] は OK）

RSQ：クエリが 1-based なら [1, n] のように 1 起点にしてください（自動判別します）

UF：answers は connected クエリのみの列。union のたびには値を出しません

MST：辺集合が同じでも 書き順が違う とハッシュが変わります。正規化→ソート→連結→SHA1 の手順で
