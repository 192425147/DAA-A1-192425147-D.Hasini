"""Generates every graph from the student's OWN results CSV files (results/results.csv, results/task12_results.csv)."""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import REG_NO, NAME

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")
OUT = os.path.join(RES, "graphs")
os.makedirs(OUT, exist_ok=True)
COL = {"Linear search": "#d62728", "Binary search (recursive)": "#1f77b4", "Hash table (chaining)": "#2ca02c"}
MARK = {"Linear search": "o", "Binary search (recursive)": "s", "Hash table (chaining)": "^"}
FOOT = f"Reg No: {REG_NO} | {NAME}"

rows = list(csv.DictReader(open(os.path.join(RES, "results.csv"))))
algs = list(COL)


def series(alg, key):
    r = sorted([x for x in rows if x["algorithm"] == alg], key=lambda x: int(x["n"]))
    return [int(x["n"]) for x in r], [float(x[key]) for x in r]


def finish(fig, name, title):
    fig.suptitle(title, fontsize=12)
    fig.text(0.99, 0.005, FOOT, ha="right", fontsize=7, color="gray")
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    fig.savefig(os.path.join(OUT, name), dpi=160)
    plt.close(fig)


# 1 time vs n
fig, ax = plt.subplots(figsize=(6.5, 4.2))
for a in algs:
    n, y = series(a, "avg_us_found")
    ax.plot(n, y, marker=MARK[a], color=COL[a], label=a)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Number of records n"); ax.set_ylabel("Average time per successful search (microseconds)")
ax.grid(True, which="both", alpha=.3); ax.legend()
finish(fig, "fig9_1_time_vs_n.png", "Average search time vs input size (log-log)")

# 2 comparisons vs n
fig, ax = plt.subplots(figsize=(6.5, 4.2))
for a in algs:
    n, y = series(a, "avg_comps_found")
    ax.plot(n, y, marker=MARK[a], color=COL[a], label=a)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Number of records n"); ax.set_ylabel("Average key comparisons per successful search")
ax.grid(True, which="both", alpha=.3); ax.legend()
finish(fig, "fig9_2_comparisons_vs_n.png", "Average number of comparisons vs input size (log-log)")

# 3 preprocessing
fig, ax = plt.subplots(figsize=(6.5, 4.2))
for a in algs[1:]:
    n, y = series(a, "preprocess_ms")
    ax.plot(n, y, marker=MARK[a], color=COL[a], label=a.split(" (")[0] + (" - sort" if "Binary" in a else " - build"))
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Number of records n"); ax.set_ylabel("Preprocessing time (milliseconds)")
ax.grid(True, which="both", alpha=.3); ax.legend()
finish(fig, "fig9_3_preprocessing_vs_n.png", "Preprocessing cost vs input size (linear search needs none)")

# 4 theory vs experiment (comparisons)
fig, axs = plt.subplots(1, 3, figsize=(11, 3.8))
for ax, a in zip(axs, algs):
    n, m = series(a, "avg_comps_found")
    _, t = series(a, "theory_avg_comps_found")
    ax.plot(n, m, marker=MARK[a], color=COL[a], label="measured (avg, found)")
    ax.plot(n, t, "k--", label="theory")
    ax.set_xscale("log")
    if a != "Hash table (chaining)":
        ax.set_yscale("log")
    else:
        ax.set_ylim(0, 2)
    ax.set_xlabel("n"); ax.set_ylabel("avg comparisons"); ax.set_title(a, fontsize=9)
    ax.grid(True, which="both", alpha=.3); ax.legend(fontsize=7)
finish(fig, "fig10_1_theory_vs_experiment.png", "Theoretical vs measured comparisons (successful search)")

# 5 theory vs experiment (time normalised by theoretical growth)
import math
fig, ax = plt.subplots(figsize=(6.5, 4.2))
for a in algs:
    n, y = series(a, "avg_us_found")
    if a == "Linear search":
        g = [v for v in n]
    elif a.startswith("Binary"):
        g = [math.log2(v) for v in n]
    else:
        g = [1 for _ in n]
    ratio = [yy / gg for yy, gg in zip(y, g)]
    ax.plot(n, [r / ratio[0] for r in ratio], marker=MARK[a], color=COL[a], label=f"{a}: time / {'n' if a.startswith('Linear') else 'log2 n' if a.startswith('Binary') else '1'}")
ax.axhline(1, color="k", ls="--", lw=.8)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Number of records n"); ax.set_ylabel("measured time / theoretical growth (normalised to n = 1000)")
ax.grid(True, which="both", alpha=.3); ax.legend(fontsize=7)
finish(fig, "fig10_2_normalised_time.png", "Does measured time follow the predicted growth? (flat line = yes)")

# 6 task 12
t12 = list(csv.DictReader(open(os.path.join(RES, "task12_results.csv"))))[:3]
names = ["Linear\n(projected)", "Binary\n(sorted array)", "Hash table"]
prep = [float(r["prep_s"]) for r in t12]
srch = [float(r["search_total_s_for_50000"]) for r in t12]
fig, ax = plt.subplots(figsize=(6.5, 4.2))
x = range(3)
ax.bar(x, srch, label="time for 50,000 searches", color="#1f77b4")
ax.bar(x, prep, bottom=srch, label="daily preprocessing", color="#ff7f0e")
ax.set_yscale("log"); ax.set_xticks(list(x)); ax.set_xticklabels(names)
ax.set_ylabel("seconds (log scale)"); ax.set_xlabel("Design")
for i in x:
    ax.text(i, (prep[i] + srch[i]) * 1.15, f"{prep[i] + srch[i]:.2f} s", ha="center", fontsize=8)
ax.grid(True, axis="y", which="both", alpha=.3); ax.legend()
finish(fig, "fig12_1_task12_total_cost.png", "Task 12: cost of 50,000 searches on 1,000,000 records")
print("graphs written to", OUT, sorted(os.listdir(OUT)))
