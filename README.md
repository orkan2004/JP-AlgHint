# JP-AlgHint v1 (WIP)
日本語アルゴリズム学習用の合成データセット。
各サンプルは 問題文 / IO仕様 / 自動採点テスト / 参照解 / 段階ヒント(Lv1-3) /
誤答例(distractors) / 機械可検証の証拠(witness) を含む。

## Quickstart

python .\gen\gcd_gen.py 30
python .\gen\bs_gen.py 30
python .\gen\int_gen.py 30
python .\eval\validate_all.py
python .\eval\linters.py
python .\eval\stats_overview.py
