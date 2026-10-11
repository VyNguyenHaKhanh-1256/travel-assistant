"""Kiểm thử mốc M0: không cần API key, không cần mạng."""
import subprocess
import sys
from pathlib import Path

import pytest

from travel.config import ROOT, get_gemini_key, load_config

CHECK_ENV = ROOT / "scripts" / "check_env.py"


def test_default_config_loads():
    cfg = load_config()
    assert cfg["timezone"] == "Asia/Ho_Chi_Minh"


def test_llm_disabled_by_default():
    # Cổng G-LLM: LLM phải tắt cho tới khi xác minh xong.
    assert load_config()["llm_enabled"] is False


def test_unverified_values_are_not_filled():
    cfg = load_config()
    assert cfg["llm_rpm"] is None
    assert cfg["max_llm_calls_per_day"] is None


def test_osrm_removed_from_config():
    assert not [k for k in load_config() if k.lower().startswith("osrm")]


def test_values_in_sane_ranges():
    cfg = load_config()
    assert 0 < cfg["tau"] < 1
    assert cfg["ttl_weather_hours"] > 0 and cfg["ttl_static_days"] > 0
    assert cfg["max_agent_steps"] >= 1 and cfg["top_k"] >= 1
    assert 0 <= cfg["rain_threshold_pct"] <= 100


def test_invalid_config_is_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("tau: 0.9\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(bad)


def test_env_example_contains_no_secret():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    values = [ln.split("=", 1)[1].strip() for ln in text.splitlines()
              if "=" in ln and not ln.lstrip().startswith("#")]
    assert values and all(v == "" for v in values)


def test_gitignore_protects_secrets_and_generated_files():
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    for needed in (".env", ".venv/", "logs/", "chroma_db/"):
        assert needed in lines


def test_get_gemini_key_returns_none_when_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert get_gemini_key(dotenv_path=tmp_path / "khong_ton_tai.env") is None


def test_minimal_structure_exists():
    for rel in ("config/default.yaml", "data", "scripts/check_env.py",
                "src/travel/__init__.py", "tests", "README.md",
                "PROJECT_STATE.md", "DECISIONS.md"):
        assert (ROOT / rel).exists(), rel


def test_check_env_script_runs_without_crashing():
    r = subprocess.run([sys.executable, str(CHECK_ENV)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    assert r.returncode in (0, 1)
    assert "Tổng kết" in r.stdout
