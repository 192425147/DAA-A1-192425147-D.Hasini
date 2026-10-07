"""Task 12 - Day-4 design challenge benchmark:
   50,000 search requests (per hour) on 1,000,000 records; new records arrive once per day.

Measures
  A. preprocessing (sort / hash build) and peak memory of each structure
  B. serving 50,000 searches with each design (linear is MEASURED on a sample and PROJECTED to 50,000)
  C. the nightly update: re-sort vs merge of the new sorted batch vs rebuild of the hash index
  D. break-even: how many searches pay back each preprocessing cost
"""
import csv, heapq, os, random, time, tracemalloc
from common import REG_NO, SEED, banner
from dataset_generator import generate, LOW, HIGH
from algo1_linear_search import linear_search
from algo2_binary_search import preprocess_sort, binary_search_recursive
from algo3_hash_table import build_hash_table

N, REQUESTS, NEW_PER_DAY, LINEAR_SAMPLE = 1_000_000, 50_000, 5_000, 100
HERE = os.path.dirname(os.path.abspath(__file__))


def serve(fn, keys):
    t = time.perf_counter()
    hits = sum(1 for k in keys if fn(k)[0] != -1)
    return time.perf_counter() - t, hits


if __name__ == "__main__":
    banner(f"TASK 12 - Re-evaluation benchmark: {REQUESTS:,} searches on {N:,} records")
    raw = generate(N)
    rng = random.Random(SEED)
    s = set(raw)
    keys = [REG_NO, REG_NO + 1]                                  # personal keys first
    while len(keys) < REQUESTS:                                  # 90 % existing, 10 % non-existing request mix
        keys.append(rng.choice(raw) if rng.random() < 0.9 else rng.randrange(LOW, HIGH + 1))
    exp_hits = sum(1 for k in keys if k in s)

    # A. preprocessing time (measured WITHOUT tracing) and memory (measured separately with tracemalloc)
    srt, t_sort = preprocess_sort(raw)
    ht, t_hash = build_hash_table(raw)
    tracemalloc.start(); _s, _ = preprocess_sort(raw)
    mem_sorted = tracemalloc.get_traced_memory()[1] / 1e6; tracemalloc.stop(); del _s
    tracemalloc.start(); _h, _ = build_hash_table(raw)
    mem_hash = tracemalloc.get_traced_memory()[1] / 1e6; tracemalloc.stop(); del _h
    print(f"\nA. Preprocessing (done once per day)")
    print(f"   sort for binary search : {t_sort:8.3f} s   extra memory ~ {mem_sorted:7.1f} MB (second list of references)")
    print(f"   hash-table build       : {t_hash:8.3f} s   extra memory ~ {mem_hash:7.1f} MB (m = {ht.m:,} buckets)")

    # B. serving 50,000 searches
    t_bin, h_bin = serve(lambda k: binary_search_recursive(srt, k), keys)
    t_has, h_has = serve(ht.search, keys)
    t_lin_s, h_lin_s = serve(lambda k: linear_search(raw, k), keys[:LINEAR_SAMPLE])
    t_lin = t_lin_s / LINEAR_SAMPLE * REQUESTS
    print(f"\nB. Serving {REQUESTS:,} searches (mix: ~90% existing keys, ~10% missing; includes own reg no + reg no+1)")
    print(f"   {'design':<34}{'prep (s)':>10}{'search total (s)':>18}{'per search (us)':>17}{'prep+search (s)':>17}{'searches/s':>12}")
    rows = [("Linear search (PROJECTED from 100)", 0.0, t_lin, t_lin / REQUESTS * 1e6),
            ("Binary search on sorted array", t_sort, t_bin, t_bin / REQUESTS * 1e6),
            ("Hash table (chaining)", t_hash, t_has, t_has / REQUESTS * 1e6)]
    for name, p, tt, us in rows:
        print(f"   {name:<34}{p:>10.3f}{tt:>18.3f}{us:>17.2f}{p + tt:>17.3f}{REQUESTS / tt:>12,.0f}")
    print(f"   correctness: hits found by binary = {h_bin:,}, hash = {h_has:,}, expected = {exp_hits:,} "
          f"-> {'MATCH' if h_bin == h_has == exp_hits else 'MISMATCH'}")
    need = REQUESTS / 3600
    print(f"   required rate = {REQUESTS:,}/hour = {need:.2f} searches/second")
    for name, p, tt, us in rows:
        ok = "meets" if REQUESTS / tt >= need else "FAILS"
        print(f"   {name:<34} capacity {REQUESTS / tt:>12,.0f}/s on one core -> {ok} the requirement"
              f"  (CPU busy {need * us / 1e6 * 100:6.3f}% of one core)")

    # C. nightly update
    new = [rng.randrange(LOW, HIGH + 1) for _ in range(NEW_PER_DAY)]
    new = [x for x in dict.fromkeys(new) if x not in s]
    t = time.perf_counter(); _ = sorted(raw + new); t_resort = time.perf_counter() - t
    new_sorted = sorted(new)
    t = time.perf_counter(); merged = list(heapq.merge(srt, new_sorted)); t_merge = time.perf_counter() - t
    t = time.perf_counter(); ht2, _ = build_hash_table(raw + new); t_rebuild = time.perf_counter() - t
    assert merged == sorted(raw + new)
    print(f"\nC. Nightly update with {len(new):,} new records (once per day)")
    print(f"   re-sort everything          : {t_resort:7.3f} s")
    print(f"   merge sorted batch (O(n+k)) : {t_merge:7.3f} s")
    print(f"   rebuild hash index          : {t_rebuild:7.3f} s")

    # D. break-even versus linear search
    saved_bin = (t_lin / REQUESTS) - (t_bin / REQUESTS)
    saved_has = (t_lin / REQUESTS) - (t_has / REQUESTS)
    print(f"\nD. Break-even against linear search (searches needed to repay preprocessing)")
    print(f"   binary search : {t_sort / saved_bin:8.1f} searches")
    print(f"   hash table    : {t_hash / saved_has:8.1f} searches")
    print(f"   searches per day at 50,000/hour = {REQUESTS * 24:,}  (preprocessing happens once per day)")
    print(f"   daily preprocessing cost per search: binary = {t_sort / (REQUESTS * 24) * 1e6:.2f} us, hash = {t_hash / (REQUESTS * 24) * 1e6:.2f} us")

    os.makedirs(os.path.join(HERE, "..", "results"), exist_ok=True)
    with open(os.path.join(HERE, "..", "results", "task12_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["design", "prep_s", "search_total_s_for_50000", "per_search_us", "memory_mb"])
        w.writerow(["Linear (projected)", 0, f"{t_lin:.4f}", f"{t_lin / REQUESTS * 1e6:.3f}", 0])
        w.writerow(["Binary", f"{t_sort:.4f}", f"{t_bin:.4f}", f"{t_bin / REQUESTS * 1e6:.3f}", f"{mem_sorted:.1f}"])
        w.writerow(["Hash", f"{t_hash:.4f}", f"{t_has:.4f}", f"{t_has / REQUESTS * 1e6:.3f}", f"{mem_hash:.1f}"])
        w.writerow(["nightly_resort_s", f"{t_resort:.4f}", "", "", ""])
        w.writerow(["nightly_merge_s", f"{t_merge:.4f}", "", "", ""])
        w.writerow(["nightly_hash_rebuild_s", f"{t_rebuild:.4f}", "", "", ""])
    print("\nresults saved to results/task12_results.csv")
