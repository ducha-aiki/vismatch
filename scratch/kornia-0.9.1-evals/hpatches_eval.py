"""HPatches viewpoint (test split) homography eval for one vismatch matcher.

Usage: hpatches_eval.py MODEL OUT.json [device] [limit]
Dataset dir: $HPATCHES (default ~/datasets/HPatchesSeq-ransac-tutorial/test), with Hgt.h5 and imgs/<seq>/<i>.ppm.
"""

import json
import os
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import h5py
import numpy as np
import torch
import kornia
import vismatch
from PIL import Image
from vismatch import get_matcher

model, out = sys.argv[1], sys.argv[2]
device = sys.argv[3] if len(sys.argv) > 3 else "cuda"
limit = int(sys.argv[4]) if len(sys.argv) > 4 else None
root = Path(os.environ.get("HPATCHES", Path.home() / "datasets/HPatchesSeq-ransac-tutorial/test"))
with h5py.File(root / "Hgt.h5") as f:
    gt = {k: f[k][()] for k in f.keys()}
keys = sorted(gt)[:limit]

torch.manual_seed(0)
m = get_matcher(model, device=device)
rows = []
for k in keys:
    seq, a, b = k.rsplit("_", 2)
    p0, p1 = root / "imgs" / seq / f"{a}.ppm", root / "imgs" / seq / f"{b}.ppm"
    torch.manual_seed(0)
    t = time.time()
    r = m(str(p0), str(p1))
    dt = time.time() - t
    w, h = Image.open(p0).size
    corners = np.array([[0, 0, 1], [w - 1, 0, 1], [w - 1, h - 1, 1], [0, h - 1, 1]], dtype=np.float64).T

    def proj(H):
        q = H @ corners
        return (q[:2] / q[2:]).T

    H = r["H"]
    err = float(np.mean(np.linalg.norm(proj(H) - proj(gt[k]), axis=1))) if H is not None else float("inf")
    rows.append(
        {
            "pair": k,
            "err": err,
            "inliers": int(r["num_inliers"]),
            "matches": len(r["matched_kpts0"]),
            "kpts0": len(r["all_kpts0"]),
            "time": dt,
        }
    )
errs = np.array([x["err"] for x in rows])
summary = {
    "model": model,
    "kornia": kornia.__version__,
    "vismatch_file": vismatch.__file__,
    "device": device,
    "n": len(rows),
    **{f"acc@{t}px": float(np.mean(errs <= t)) for t in (1, 3, 5, 10)},
    "median_err": float(np.median(errs)),
    "mean_inliers": float(np.mean([x["inliers"] for x in rows])),
    "mean_matches": float(np.mean([x["matches"] for x in rows])),
    "mean_kpts": float(np.mean([x["kpts0"] for x in rows])),
    "sec_per_pair": float(np.mean([x["time"] for x in rows[1:]] or [rows[0]["time"]])),
}
json.dump({"summary": summary, "rows": rows}, open(out, "w"), indent=1)
print(json.dumps(summary))
