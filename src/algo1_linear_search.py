# Reg No: 192425147 | Name: D.Hasini
"""Algorithm 1 - Linear (sequential) search.  Strategy: brute force, ITERATIVE.
Preprocessing: none.  Works on the raw, unsorted records.
Returns (index or -1, number of key comparisons)."""


def linear_search(a, key):
    for i in range(len(a)):
        if a[i] == key:            # <-- BASIC OPERATION: key comparison
            return i, i + 1        # i+1 comparisons were executed
    return -1, len(a)              # unsuccessful: all n comparisons executed
