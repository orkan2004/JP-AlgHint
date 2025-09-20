# JP-AlgHint

- JSON スキーマ: docs/schema.json, eval/schema.json
- バリデーション: python eval/validate_all.py
- ID パターン: ^(GCD|BS|INT|BFS|KNAP|DSIM|MST|RSQ|UF)_\d{8}_\d{5}$

## 開発フロー
1. ブランチ作成: git switch -c feature/<topic>
2. 変更 → コミット → git push -u origin feature/<topic>
3. GitHub で PR を作成（CI が通ったらレビュー＆マージ）
