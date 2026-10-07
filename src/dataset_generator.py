"""Dataset generator: unique 9-digit registration numbers, seeded with the last 4 digits of the reg no.

Guarantees for every dataset:
  * all registration numbers are unique and stored in RANDOM (unsorted) order
  * the student's own reg no (192425147) IS present            -> 'found' test key
  * reg no + 1 (192425148) is NOT present                       -> 'not found' test key

Usage:  python dataset_generator.py --n 1000 --out ../data/sample_1000.csv
"""
import argparse, csv, random
from common import REG_NO, SEED, banner

LOW, HIGH = 100_000_000, 999_999_999      # all 9-digit numbers (900 million possible reg numbers)


def generate(n, seed=SEED, reg_no=REG_NO):
    rng = random.Random(seed + n)           # same seed rule, different n -> different but reproducible
    banned = {reg_no, reg_no + 1}
    pool = rng.sample(range(LOW, HIGH + 1), n + 2)
    data = [x for x in pool if x not in banned][: n - 1]
    data.insert(rng.randint(0, len(data)), reg_no)   # own reg no at a random position
    assert len(data) == n and len(set(data)) == n and reg_no + 1 not in set(data)
    return data


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--out", default=None, help="optional CSV path")
    args = ap.parse_args()
    banner(f"Dataset generator  (n = {args.n:,})")
    d = generate(args.n)
    print(f"generated {len(d):,} unique reg numbers; min={min(d)} max={max(d)}")
    print(f"own reg no {REG_NO} present: {REG_NO in set(d)} | reg no+1 present: {REG_NO + 1 in set(d)}")
    if args.out:
        with open(args.out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["record_id", "reg_no"])
            for i, x in enumerate(d):
                w.writerow([i, x])
        print("written:", args.out)
