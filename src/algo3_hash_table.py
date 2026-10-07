"""Algorithm 3 - Hash table with separate chaining.  Strategy: space-time trade-off (hashing).
Preprocessing: build the table once - n insertions, O(n) expected.
h(k) = k mod m, m = prime >= n / 0.75  (load factor alpha <= 0.75).
Returns (record position or -1, number of key comparisons inside the chain)."""
import time


def _is_prime(x):
    if x < 2:
        return False
    i = 2
    while i * i <= x:
        if x % i == 0:
            return False
        i += 1
    return True


def _next_prime(x):
    while not _is_prime(x):
        x += 1
    return x


class HashTable:
    def __init__(self, n_expected, max_load=0.75):
        self.m = _next_prime(int(n_expected / max_load) + 1)
        self.buckets = [None] * self.m
        self.size = 0

    def insert(self, key, pos):
        h = key % self.m                      # hash function
        b = self.buckets[h]
        if b is None:
            self.buckets[h] = [(key, pos)]
        else:
            b.append((key, pos))              # chaining (duplicates not expected: reg nos are unique)
        self.size += 1

    def search(self, key):
        b = self.buckets[key % self.m]        # 1 hash computation, O(1) index
        c = 0
        if b is not None:
            for k, pos in b:
                c += 1
                if k == key:                  # <-- BASIC OPERATION: key comparison inside the chain
                    return pos, c
        return -1, c


def build_hash_table(a):
    """Preprocessing step. Returns (table, seconds)."""
    t = time.perf_counter()
    ht = HashTable(len(a))
    for pos, key in enumerate(a):
        ht.insert(key, pos)
    return ht, time.perf_counter() - t
