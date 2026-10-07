"""Algorithm 2 - Binary search.  Strategy: decrease-and-conquer / divide-and-conquer, RECURSIVE.
Preprocessing: the records must be SORTED once (O(n log n)).
Returns (index or -1, number of key comparisons).  One 3-way comparison (==, <, >) per call = 1 comparison."""
import time


def preprocess_sort(a):
    """Preprocessing step (included in the efficiency analysis). Returns (sorted_copy, seconds)."""
    t = time.perf_counter()
    s = sorted(a)
    return s, time.perf_counter() - t


def binary_search_recursive(a, key, low=0, high=None):
    if high is None:
        high = len(a) - 1
    if low > high:                          # base case: empty range -> not found
        return -1, 0
    mid = (low + high) // 2
    if a[mid] == key:                       # <-- BASIC OPERATION: key comparison (3-way)
        return mid, 1
    if a[mid] < key:
        idx, c = binary_search_recursive(a, key, mid + 1, high)   # ONE recursive call on ~n/2 elements
    else:
        idx, c = binary_search_recursive(a, key, low, mid - 1)
    return idx, c + 1


def binary_search_iterative(a, key):
    """Iterative form of the SAME strategy (used only to cross-check the recursive one; not a 4th approach)."""
    low, high, c = 0, len(a) - 1, 0
    while low <= high:
        mid = (low + high) // 2
        c += 1
        if a[mid] == key:
            return mid, c
        if a[mid] < key:
            low = mid + 1
        else:
            high = mid - 1
    return -1, c
