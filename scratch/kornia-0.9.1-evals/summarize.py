"""Print a markdown table comparing <model>.base.json and <model>.new.json in a results dir."""

import json
import sys
from pathlib import Path

out = Path(sys.argv[1])
cols = ["acc@1px", "acc@3px", "acc@5px", "median_err", "mean_inliers", "mean_kpts", "sec_per_pair"]
print("| model | tree | kornia | " + " | ".join(cols) + " |")
print("|---|---|---|" + "---|" * len(cols))
for base in sorted(out.glob("*.base.json")):
    model = base.name[: -len(".base.json")]
    for tree in ("base", "new"):
        p = out / f"{model}.{tree}.json"
        if not p.exists():
            print(f"| {model} | {tree} | missing |" + " |" * len(cols))
            continue
        s = json.load(open(p))["summary"]
        vals = [
            f"{s[c]:.3f}" if c.startswith("acc") or c in ("median_err", "sec_per_pair") else f"{s[c]:.0f}" for c in cols
        ]
        print(f"| {model} | {tree} | {s['kornia']} | " + " | ".join(vals) + " |")
