# kornia 0.9.1 migration: tests and evals

Scratch tooling for the `kornia-0.9.1` branch. Not meant to be merged.

## Setup (CUDA box)

```bash
git clone --recurse-submodules -b kornia-0.9.1 https://github.com/ducha-aiki/vismatch.git
cd vismatch
git fetch origin kornia-0.9.1-evals && git worktree add ../vismatch-evals origin/kornia-0.9.1-evals
uv venv .venv --python 3.11 && VIRTUAL_ENV=.venv uv pip install -e . pytest pytest-timeout h5py
```

HPatches viewpoint test split (507 MB, only `imgs/` and `Hgt.h5` are read), e.g. from the Mac:

```bash
rsync -a mac:datasets/HPatchesSeq-ransac-tutorial/test/{imgs,Hgt.h5} ~/datasets/HPatchesSeq-ransac-tutorial/test/
export HPATCHES=~/datasets/HPatchesSeq-ransac-tutorial/test
```

## Tests

```bash
# fast, no weights
.venv/bin/python -m pytest tests/test_kornia_compat.py tests/test_utils.py tests/test_viz.py tests/test_import_sandbox.py -q
# matchers touched by the migration (instantiation errors are reported as skips: read -rs)
.venv/bin/python -m pytest tests/test_matchers.py -rs --timeout=600 -k \
  "loftr or matchformer or aspanformer or topicfm or matchanything or xfeat or lightglue or dedode or doghardnet or ripe or gim or roma or silk or ufm or dad or liftfeat or rdd or minima"
# everything, as CI does
.venv/bin/python -m pytest tests -vv -rs --timeout=300
```

## Evals: main + kornia 0.8.2 vs this branch + kornia 0.9.1

```bash
E=../vismatch-evals/scratch/kornia-0.9.1-evals
$E/setup_baseline.sh . ~/kornia091-evals
$E/run_all.sh . ~/kornia091-evals cuda \
  disk-lightglue aliked-lightglue xfeat xfeat-star xfeat-lightglue \
  sift-lightglue doghardnet-lightglue superpoint-lightglue dedode-lightglue dedode-kornia loftr eloftr
```

`run_all.sh` prints one line per run and finally a markdown table (`summarize.py`): homography accuracy at
1/3/5 px mean corner error, median error, mean inliers, mean keypoints and seconds per pair over the 145 pairs.
Expected: identical or near-identical numbers for the matchers whose code did not change (sift-, doghardnet-,
superpoint-lightglue, loftr, eloftr through the `kornia.utils.grid` shim); small differences for the ones switched
to kornia (disk-, aliked-lightglue, the xfeat family). Cleanup: `rm ~/kornia091-evals/base/vismatch/third_party && git worktree remove --force ~/kornia091-evals/base`.
