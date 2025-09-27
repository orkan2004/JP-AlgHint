# eval/verify_witness.py
import json, glob, os

def verify_bfs(item):
    w = item.get("witness", {})
    ok = isinstance(w.get("shortest_len"), int) and isinstance(w.get("parent_hash",""), str)
    return ok, ("BFS witness format ok" if ok else "BFS witness missing/invalid")

def verify_int(item):
    w = item.get("witness", {})
    ints = w.get("chosen_intervals", [])
    try:
        ints = [tuple(x) for x in ints]
    except Exception:
        return False, "INT witness invalid format"
    ok = True
    last_end = -10**18
    for s,e in sorted(ints, key=lambda x:(x[1],x[0])):
        if s < last_end:
            ok = False; break
        last_end = e
    return ok, ("INT non-overlap ok" if ok else "INT overlap found")

def main():
    paths = glob.glob("data/**/*.json", recursive=True)
    total = passed = 0
    os.makedirs("eval", exist_ok=True)
    with open("eval/witness_report.txt","w",encoding="utf-8") as out:
        for p in paths:
            try:
                item = json.load(open(p,"r",encoding="utf-8"))
                _id = item.get("id","")
                fam = _id.split("_",1)[0] if "_" in _id else ""
                ok, msg = True, "skip"
                if fam == "BFS": ok, msg = verify_bfs(item)
                elif fam == "INT": ok, msg = verify_int(item)
                total += 1; passed += int(ok)
                out.write(f"{_id}\t{fam}\t{ok}\t{msg}\n")
            except Exception as e:
                out.write(f"{p}\t?\tFalse\terror: {e!r}\n")
        out.write(f"\nTOTAL {passed}/{total}\n")
    print(f"Witness check: {passed}/{total}")

if __name__ == "__main__":
    main()
