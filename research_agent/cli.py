"""Controlled experiment launcher. No arbitrary commands or remote execution."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

MAX_TIMEOUT = 4 * 60 * 60
ALLOWED_BUGS = {"Time-25", "Chart-1", "Lang-1"}
ALLOWED_MODELS = {"llama3.1:8b", "qwen2:7b", "mistral:7b"}


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("template") != "defects4j_wp1":
        raise ValueError("Only the approved defects4j_wp1 template is supported")
    bugs = config.get("bugs")
    models = config.get("models")
    if not isinstance(bugs, list) or not bugs or len(bugs) > 3 or any(b not in ALLOWED_BUGS for b in bugs):
        raise ValueError("Choose 1-3 approved bugs")
    if not isinstance(models, list) or not models or len(models) > 3 or any(m not in ALLOWED_MODELS for m in models):
        raise ValueError("Choose 1-3 approved model tags")
    if config.get("backend") != "ollama":
        raise ValueError("Only local Ollama backend is enabled in this scaffold")
    timeout = config.get("timeout_seconds", MAX_TIMEOUT)
    if type(timeout) is not int or timeout < 1 or timeout > MAX_TIMEOUT:
        raise ValueError("Timeout must be between 1 and 14400 seconds")
    return config


def build_command(config: dict, workspace: Path) -> list[str]:
    workspace = workspace.resolve()
    runner = workspace / "wp1" / "run_wp1_benchmark.py"
    if not runner.is_file():
        raise FileNotFoundError(f"Benchmark script not found: {runner}")
    flexfl = workspace / "references" / "FlexFL_OriginalReplication"
    if not flexfl.is_dir():
        raise FileNotFoundError(f"FlexFL dependency not found: {flexfl}")
    return [sys.executable, str(runner), "--flexfl-repo", str(flexfl),
            "--backend", "ollama", "--models", ",".join(config["models"]),
            "--bugs", ",".join(config["bugs"])]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Safe AdaptiveContextOpt experiment controller")
    parser.add_argument("action", choices=["plan", "run"])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--execute", action="store_true", help="Explicitly allow benchmark execution")
    args = parser.parse_args(argv)
    config = load_config(args.config)
    if args.action == "run" and not args.execute:
        parser.error("Running experiments requires --execute")
    if args.action == "run" and args.workspace is None:
        parser.error("Running experiments requires --workspace")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path("runs") / (timestamp + "-" + os.urandom(3).hex())
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "plan.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    if args.action == "plan":
        print(f"Plan saved: {run_dir / 'plan.json'} (nothing executed)")
        return 0
    workspace = args.workspace.resolve()
    # Never run against the original repo unless user explicitly cloned it to an isolated directory.
    if not (workspace / ".git").exists():
        raise RuntimeError("Workspace must be a separate Git clone")
    command = build_command(config, workspace)
    (run_dir / "command.json").write_text(json.dumps(command, indent=2), encoding="utf-8")
    print(f"Running approved benchmark in {workspace}; logs: {run_dir}", flush=True)
    with (run_dir / "stdout.log").open("w") as stdout, (run_dir / "stderr.log").open("w") as stderr:
        try:
            result = subprocess.run(command, cwd=workspace, stdout=stdout, stderr=stderr,
                                    timeout=config.get("timeout_seconds", MAX_TIMEOUT), check=False)
            status = {"returncode": result.returncode, "timed_out": False}
        except subprocess.TimeoutExpired:
            status = {"returncode": None, "timed_out": True}
    (run_dir / "status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(f"Result: {status}")
    return 1 if status["returncode"] != 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
