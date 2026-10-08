#!/usr/bin/env bash
#SBATCH --job-name=context-research-smoke
#SBATCH --time=04:00:00
#SBATCH --gres=gpu:1
#SBATCH --output=slurm-%j.out
set -euo pipefail
# Template only. Verify AIScalar partitions, GPU requests, and resource rules.
# Run from the NEW research-agent repo and ensure an isolated workspace exists.
source .venv/bin/activate
python -m research_agent.cli run \
  --config configs/defects4j_smoke.json \
  --workspace workspaces/AdaptiveContextOpt \
  --execute
