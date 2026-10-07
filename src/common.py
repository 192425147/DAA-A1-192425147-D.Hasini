"""Shared identity + helpers used by every script (so every output prints Reg No / Name / date)."""
import datetime

REG_NO = 192425147
NAME = "D.Hasini"
SEED = int(str(REG_NO)[-4:])          # personal seed = last 4 digits of reg no -> 5147
SIZES = [1_000, 10_000, 100_000, 1_000_000]


def banner(title=""):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"Reg No: {REG_NO} | Name: {NAME} | Seed: {SEED} | {now}"
    print(line)
    if title:
        print(title)
    print("=" * max(len(line), len(title)))
