"""Task 8 - correctness tests for all three algorithms on 1K, 10K, 100K, 1M records.
Every result is checked against an independent oracle (a Python dict built from the raw data)."""
import random, sys
from common import REG_NO, NAME, SEED, SIZES, banner
from dataset_generator import generate
from algo1_linear_search import linear_search
from algo2_binary_search import preprocess_sort, binary_search_recursive, binary_search_iterative
from algo3_hash_table import build_hash_table

passed = failed = 0


def check(label, ok):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        print("   FAIL:", label)


def run_size(n):
    global passed, failed
    p0, f0 = passed, failed
    raw = generate(n)
    oracle = {k: i for i, k in enumerate(raw)}
    srt, t_sort = preprocess_sort(raw)
    ht, t_hash = build_hash_table(raw)
    rng = random.Random(SEED)
    found_keys = [REG_NO, raw[0], raw[-1], srt[0], srt[-1], srt[(n - 1) // 2]] + rng.sample(raw, 20)
    missing = [REG_NO + 1, 0, srt[0] - 1, srt[-1] + 1, 999_999_999, srt[len(srt) // 2] + 1]
    missing = [m for m in missing if m not in oracle]
    for k in found_keys:                       # keys that exist
        i, _ = linear_search(raw, k);                  check(f"linear found {k}", i != -1 and raw[i] == k)
        i, _ = binary_search_recursive(srt, k);        check(f"binary-rec found {k}", i != -1 and srt[i] == k)
        i, _ = binary_search_iterative(srt, k);        check(f"binary-it found {k}", i != -1 and srt[i] == k)
        i, _ = ht.search(k);                           check(f"hash found {k}", i == oracle[k])
    for k in missing:                          # keys that do not exist
        check(f"linear missing {k}", linear_search(raw, k)[0] == -1)
        check(f"binary-rec missing {k}", binary_search_recursive(srt, k)[0] == -1)
        check(f"binary-it missing {k}", binary_search_iterative(srt, k)[0] == -1)
        check(f"hash missing {k}", ht.search(k)[0] == -1)
    cases = len(found_keys) + len(missing)
    status = "ALL PASS" if failed == f0 else "FAILURES"
    print(f"n = {n:>9,} | test keys = {cases:>2} (found {len(found_keys)}, not found {len(missing)}) "
          f"| own reg no found: {linear_search(raw, REG_NO)[0] != -1} | reg no+1 found: {linear_search(raw, REG_NO + 1)[0] != -1} "
          f"| checks {passed - p0 + failed - f0} -> {status}")


if __name__ == "__main__":
    banner("TASK 8 - Correctness tests: Linear | Binary (recursive + iterative check) | Hash table")
    # edge cases
    check("empty list linear", linear_search([], 5)[0] == -1)
    check("empty list binary", binary_search_recursive([], 5)[0] == -1)
    one = [REG_NO]
    check("single linear", linear_search(one, REG_NO)[0] == 0)
    check("single binary", binary_search_recursive(one, REG_NO)[0] == 0)
    check("single binary miss", binary_search_recursive(one, REG_NO + 1)[0] == -1)
    print(f"edge cases (empty list, single element)       -> {'ALL PASS' if failed == 0 else 'FAILURES'}")
    for n in SIZES:
        run_size(n)
    print("-" * 70)
    print(f"TOTAL checks: {passed + failed} | passed: {passed} | failed: {failed}")
    print("RESULT:", "ALL ALGORITHMS CORRECT" if failed == 0 else "SOME TESTS FAILED")
    sys.exit(0 if failed == 0 else 1)
