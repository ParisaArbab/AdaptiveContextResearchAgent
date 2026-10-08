import json
from pathlib import Path
import pytest
from research_agent.cli import load_config, build_command, main


def test_valid_config():
    cfg = load_config(Path("configs/defects4j_smoke.json"))
    assert cfg["bugs"] == ["Time-25"]


def test_rejects_unknown_template(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"template": "shell", "bugs": ["Time-25"], "models": ["llama3.1:8b"], "backend": "ollama"}))
    with pytest.raises(ValueError):
        load_config(p)


def test_rejects_unapproved_model(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"template": "defects4j_wp1", "bugs": ["Time-25"], "models": ["danger; rm -rf"], "backend": "ollama"}))
    with pytest.raises(ValueError):
        load_config(p)


def test_plan_does_not_execute(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"template": "defects4j_wp1", "bugs": ["Time-25"], "models": ["llama3.1:8b"], "backend": "ollama"}))
    assert main(["plan", "--config", str(cfg)]) == 0
    assert len(list((tmp_path / "runs").glob("*/plan.json"))) == 1
