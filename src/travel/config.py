"""Đọc cấu hình và khóa API. Không in, không ghi log khóa API."""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "config" / "default.yaml"

# Khóa bắt buộc và kiểu dữ liệu. None được phép với các khóa trong NULLABLE.
REQUIRED = {
    "llm_enabled": bool,
    "llm_backend": str,
    "llm_timeout_s": (int, float),
    "llm_rpm": (int, float),
    "max_llm_calls_per_day": (int, float),
    "max_agent_steps": int,
    "embedding_model": str,
    "tau": (int, float),
    "ttl_weather_hours": (int, float),
    "ttl_static_days": (int, float),
    "top_k": int,
    "tool_timeout_s": (int, float),
    "rain_threshold_pct": (int, float),
    "forecast_horizon_days": int,
    "route_circuity": (int, float),
    "route_speed_kmh": (int, float),
    "timezone": str,
    "random_seed": int,
}
NULLABLE = {"llm_timeout_s", "llm_rpm", "max_llm_calls_per_day"}


def load_config(path=None) -> dict:
    """Đọc YAML và kiểm tra khóa/kiểu dữ liệu. Ném ValueError nếu sai."""
    path = Path(path) if path else DEFAULT_CONFIG
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    problems = []
    for key, typ in REQUIRED.items():
        if key not in cfg:
            problems.append(f"thiếu khóa: {key}")
            continue
        val = cfg[key]
        if val is None:
            if key not in NULLABLE:
                problems.append(f"{key} không được để trống (null)")
            continue
        if isinstance(val, bool) and typ is not bool:
            problems.append(f"{key} phải là số/chuỗi, không phải true/false")
        elif not isinstance(val, typ):
            problems.append(f"{key} sai kiểu dữ liệu: {type(val).__name__}")
    if problems:
        raise ValueError("Cấu hình không hợp lệ: " + "; ".join(problems))
    return cfg


def get_gemini_key(dotenv_path=None):
    """Trả về khóa Gemini từ biến môi trường/.env, hoặc None nếu chưa có."""
    load_dotenv(dotenv_path or ROOT / ".env")
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return key or None
