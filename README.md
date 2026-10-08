# AdaptiveContext Research Agent

An **independent, safety-first** experiment controller for [AdaptiveContextOpt](https://github.com/ParisaArbab/AdaptiveContextOpt). This repository does not modify the original repository.

## Safety defaults

- Private GitHub repository recommended.
- `plan` only writes an experiment plan. It never runs benchmarks.
- `run` requires `--execute` and a dedicated `--workspace` directory with a cloned copy of AdaptiveContextOpt.
- Only approved experiment templates are accepted. No LLM-generated shell commands are executed.
- Maximum one job at a time by default, with time limits enforced by the scheduler or local timeout.
- Research-generated changes should be proposed as pull requests, never merged automatically.
- Do not commit model weights, raw datasets, credentials, `.env` files, or experiment outputs.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
```

Clone a **separate working copy** of the original repository:

```bash
mkdir -p workspaces
git clone https://github.com/ParisaArbab/AdaptiveContextOpt.git workspaces/AdaptiveContextOpt
```

Make a plan without running code:

```bash
python -m research_agent.cli plan --config configs/defects4j_smoke.json
```

Run one small benchmark in the separate copy, only when dependencies and permissions are ready:

```bash
python -m research_agent.cli run --config configs/defects4j_smoke.json \
  --workspace workspaces/AdaptiveContextOpt --execute
```

The runner uses the **existing** `wp1/run_wp1_benchmark.py` command and writes its own controller logs to `runs/`. The original project may also write evaluation artifacts under its own `results/` directory in the cloned working copy.

## On AIScalar

Use your ordinary account and your institution's permitted job scheduler. The included SLURM template is a starting point: adjust partition, environment, time and GPU resources with your administrator's guidance. The research agent never needs sudo. Do not run persistent GPU jobs on a shared login node.

## Roadmap

1. Validate RAW vs LeanCTX on `Time-25` with the current upstream pipeline.
2. Add result ingestion of `summary.json`, Top-5, MAP, MRR, tokens and compression tax.
3. Add literature search and hypothesis generation, with source citations.
4. Add controlled experimental code generation on isolated Git branches.
5. Submit bounded jobs through an approved scheduler and propose PRs for review.

**Current status:** stage 1 scaffold. Automatic literature search, code changes, and experiment evaluation are **not implemented yet**.
