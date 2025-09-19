import json, random, time
from pathlib import Path

TODAY = time.strftime("%Y%m%d")

def new_id(seq:int): 
    return f"BS_{TODAY}_{seq:05d}"

def make_strict_increasing(n, r: random.Random, low=0, high=10**6):
    arr = sorted(r.sample(range(low, high), n))
    return arr

def pick_absent(r: random.Random, arr, low=0, high=10**6):
    s = set(arr)
    while True:
        x = r.randrange(low, high)
        if x not in s: return x

def make_item(seq:int, r: random.Random):
    n = r.randint(5, 30)
    arr = make_strict_increasing(n, r)
    present = r.choice(arr)
    absent  = pick_absent(r, arr)
    tests = [
        {"in": f"{n}\n{' '.join(map(str,arr))}\n{present}\n", "out": "1\n"},
        {"in": f"{n}\n{' '.join(map(str,arr))}\n{absent}\n",  "out": "0\n"}
    ]
    return {
      "id": new_id(seq),
      "task": "binary_search",
      "statement_ja": "長さ n の昇順配列と値 x が与えられる。x が存在すれば 1、なければ 0 を出力せよ。",
      "io_spec": {"input": "n\\nA_1 ... A_n\\nx", "output": "1 or 0"},
      "instance": {"seed": seq, "template_id": "BS_T1", "params": {"n": n}},
      "tests": tests,
      "reference": {"py": "ref/py/binary_search.py"},
      "hints": [
        {"level":1, "text":"配列は昇順。中央要素と x を比較し、探索区間を半分にせよ。"},
        {"level":2, "text":"左端 l、右端 r（半開区間や閉区間のどちらか）を一貫して保つ。"},
        {"level":3, "text":"bisect_left の挙動：最左の挿入位置 i を得て、A[i]==x なら発見。"}
      ],
      "distractors":[
        {"code":"OFF_BY_ONE","desc":"区間が閉/半開の取り違えで1つ外す"}
      ],
      "witness":{"present_value": present, "absent_value": absent},
      "difficulty":{"score":0.3,"basis":"log2(n) 回の分岐"},
      "tags":["search","beginner"],
      "license":"CC BY-SA 4.0 (texts) / MIT (code)"
    }

def main(n=30):
    Path("data/json").mkdir(parents=True, exist_ok=True)
    r = random.Random(4242)
    for i in range(1, n+1):
        item = make_item(i, r)
        path = Path("data/json") / f"{item['id']}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
    print(f"generated {n} BS items for {TODAY}")

if __name__=="__main__":
    import sys
    n = int(sys.argv[1]) if len(sys.argv)>1 else 30
    main(n)
