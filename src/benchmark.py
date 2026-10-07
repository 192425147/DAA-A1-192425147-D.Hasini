"""Task 9 - experimental performance of the three algorithms.

python benchmark.py --n 1000        (one size; prints terminal output + updates ../results/results.csv)
python benchmark.py --all           (all four sizes)

Measured per algorithm and size:
  preprocessing time, average time per search (found / not found), average comparisons (found / not found),
  best-case and worst-case comparisons (+ personal keys: own reg no = found, reg no + 1 = not found).
Search keys: the same random sample of existing keys (seeded) is used for every algorithm.
"""
import argparse, csv, os, random, time
from common import REG_NO, SEED, SIZES, banner
from dataset_generator import generate, LOW, HIGH
from algo1_linear_search import linear_search
from algo2_binary_search import preprocess_sort, binary_search_recursive
from algo3_hash_table import build_hash_table

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "..", "results", "results.csv")
FIELDS = ["algorithm", "n", "queries_found", "queries_notfound", "preprocess_ms", "avg_us_found", "avg_us_notfound",
          "avg_comps_found", "avg_comps_notfound", "best_comps", "worst_comps", "theory_avg_comps_found",
          "theory_worst_comps"]
Q = 1000                                                   # queries per algorithm (binary, hash)
Q_LINEAR = {1_000: 1000, 10_000: 1000, 100_000: 1000, 1_000_000: 100}   # linear is O(n): fewer queries at 1M



def timed(fn, a, keys, repeats):
    best, comps = None, 0
    for _ in range(repeats):
        t = time.perf_counter()
        total = 0
        for k in keys:
            total += fn(a, k)[1]
        el = time.perf_counter() - t
        best = el if best is None else min(best, el)
        comps = total
    return best / len(keys) * 1e6, comps / len(keys)          # (microseconds per search, comparisons per search)


def run(n):
    raw = generate(n)
    q, ql = Q, Q_LINEAR[n]
    rng = random.Random(SEED)
    found = [REG_NO] + rng.sample(raw, q - 1)                  # includes own reg no
    notfound = [REG_NO + 1] + [rng.randrange(LOW, HIGH + 1) for _ in range(q - 1)]
    s = set(raw)
    notfound = [k for k in notfound if k not in s]
    rep = 3 if n <= 10_000 else 1
    rows = []

    # ---- Algorithm 1: linear (no preprocessing)
    uf, cf = timed(linear_search, raw, found[:ql], rep)
    un, cn = timed(linear_search, raw, notfound[:ql], rep)
    best = linear_search(raw, raw[0])[1]
    worst = linear_search(raw, REG_NO + 1)[1]
    rows.append(["Linear search", n, len(found[:ql]), len(notfound[:ql]), 0.0, uf, un, cf, cn, best, worst, (n + 1) / 2, n])

    # ---- Algorithm 2: binary (preprocess = sort)
    srt, t_sort = preprocess_sort(raw)
    uf, cf = timed(binary_search_recursive, srt, found, rep)
    un, cn = timed(binary_search_recursive, srt, notfound, rep)
    best = binary_search_recursive(srt, srt[(n - 1) // 2])[1]
    worst = max(binary_search_recursive(srt, k)[1] for k in notfound)
    import math
    rows.append(["Binary search (recursive)", n, len(found), len(notfound), t_sort * 1e3, uf, un, cf, cn, best, worst,
                 math.log2(n + 1) - 1, math.floor(math.log2(n)) + 1])

    # ---- Algorithm 3: hash table (preprocess = build)
    ht, t_build = build_hash_table(raw)
    uf, cf = timed(lambda a, k: ht.search(k), None, found, rep)
    un, cn = timed(lambda a, k: ht.search(k), None, notfound, rep)
    lens = [(len(b), i) for i, b in enumerate(ht.buckets) if b]
    longest, li = max(lens)
    worst_found = ht.search(ht.buckets[li][-1][0])[1]
    worst_nf = ht.search(li)[1]                                # key = bucket index < 190M -> never present, scans longest chain
    alpha = n / ht.m
    rows.append(["Hash table (chaining)", n, len(found), len(notfound), t_build * 1e3, uf, un, cf, cn, 1,
                 max(worst_found, worst_nf), 1 + alpha / 2, longest])
    return rows, ht, raw


def save(rows):
    existing = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH) as f:
            existing = list(csv.DictReader(f))
    ns = {str(r[1]) for r in rows}
    existing = [r for r in existing if r["n"] not in ns]
    for r in rows:
        existing.append(dict(zip(FIELDS, r)))
    existing.sort(key=lambda r: (int(r["n"]), r["algorithm"]))
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in existing:
            w.writerow({k: (f"{float(v):.4f}" if k not in ("algorithm", "n", "queries_found", "queries_notfound") else v)
                        for k, v in r.items()})


def report(n, rows, ht):
    print(f"\nDataset size n = {n:,}  (seed {SEED}; own reg no {REG_NO} = found, {REG_NO + 1} = not found)")
    print(f"{'Algorithm':<27}{'prep(ms)':>11}{'us/search':>11}{'comps(found)':>14}{'comps(miss)':>13}{'best':>6}{'worst':>8}")
    print("-" * 91)
    for r in rows:
        print(f"{r[0]:<27}{r[4]:>11.2f}{r[5]:>11.2f}{r[7]:>14.2f}{r[8]:>13.2f}{r[9]:>6.0f}{r[10]:>8.0f}")
    print(f"(hash table: m = {ht.m:,} buckets, load factor = {n / ht.m:.3f}; timings = mean per search; "
          f"queries: linear {rows[0][2]}, binary/hash {rows[1][2]})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    banner("TASK 9 - Benchmark: Linear vs Binary (recursive) vs Hash table")
    for n in (SIZES if args.all else [args.n or 1000]):
        rows, ht, _ = run(n)
        report(n, rows, ht)
        save(rows)
    print("\nresults saved to results/results.csv")
