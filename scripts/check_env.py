r"""Kiểm tra môi trường máy cho dự án. Không cần mạng, không cần API key.

Chạy:  python scripts\check_env.py
Kết quả được in ra màn hình và lưu vào logs\env_report.txt (UTF-8).
"""
import importlib.util
import os
import platform
import shutil
import struct
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
MIN_PY = (3, 10)        # giả định thiết kế
WARN_RAM_GB = 8         # giả định thiết kế
WARN_DISK_GB = 5        # giả định thiết kế

lines = []
counts = {"OK": 0, "CẢNH BÁO": 0, "LỖI": 0, "GỢI Ý": 0, "THÔNG TIN": 0}


def say(level, msg):
    counts[level] += 1
    line = f"[{level}] {msg}"
    lines.append(line)
    print(line)


def total_ram_gb():
    try:
        if os.name == "nt":
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return stat.ullTotalPhys / 1024 ** 3
        with open("/proc/meminfo", encoding="utf-8") as f:
            for ln in f:
                if ln.startswith("MemTotal:"):
                    return int(ln.split()[1]) / 1024 ** 2
    except Exception:
        return None
    return None


def main():
    print("=== Kiểm tra môi trường ===")
    v = sys.version_info
    ver = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) < MIN_PY:
        say("LỖI", f"Python {ver} quá cũ; cần từ {MIN_PY[0]}.{MIN_PY[1]} trở lên.")
    elif (v.major, v.minor) >= (3, 13):
        say("CẢNH BÁO", f"Python {ver}: chưa xác minh các thư viện ở mốc sau (embedding, ChromaDB) đã hỗ trợ bản này. Khuyến nghị 3.11 hoặc 3.12.")
    else:
        say("OK", f"Python {ver}")

    bits = struct.calcsize("P") * 8
    say("OK" if bits == 64 else "CẢNH BÁO", f"Python {bits}-bit" + ("" if bits == 64 else " (nên dùng 64-bit cho thư viện ML ở mốc sau)"))

    in_venv = sys.prefix != sys.base_prefix
    say("OK" if in_venv else "CẢNH BÁO", "Đang chạy trong môi trường ảo (.venv)" if in_venv else "KHÔNG ở trong môi trường ảo; hãy kích hoạt .venv trước khi cài thư viện.")

    say("THÔNG TIN", f"Hệ điều hành: {platform.system()} {platform.release()} ({platform.machine()})")
    say("THÔNG TIN", f"Số lõi CPU (logic): {os.cpu_count()}")

    ram = total_ram_gb()
    if ram is None:
        say("CẢNH BÁO", "Không đọc được dung lượng RAM.")
    elif ram < WARN_RAM_GB:
        say("CẢNH BÁO", f"RAM {ram:.1f} GB, thấp hơn giả định thiết kế ({WARN_RAM_GB} GB). Chưa biết có đủ cho embedding hay không; sẽ đo ở M0 (bước embedding).")
    else:
        say("OK", f"RAM {ram:.1f} GB")

    free = shutil.disk_usage(ROOT).free / 1024 ** 3
    say("OK" if free >= WARN_DISK_GB else "CẢNH BÁO", f"Ổ đĩa trống {free:.1f} GB" + ("" if free >= WARN_DISK_GB else f" (giả định thiết kế cần khoảng {WARN_DISK_GB} GB)"))

    p = str(ROOT)
    if not p.isascii() or " " in p:
        say("CẢNH BÁO", f"Đường dẫn dự án có dấu/khoảng trắng: {p}. Nên chuyển tới thư mục như C:\\dev\\smart-travel để tránh lỗi công cụ.")
    elif "onedrive" in p.lower():
        say("CẢNH BÁO", "Dự án nằm trong OneDrive; nên đặt ngoài OneDrive (ví dụ C:\\dev) để tránh xung đột đồng bộ file.")
    else:
        say("OK", f"Đường dẫn dự án: {p}")

    for mod, label in (("yaml", "PyYAML"), ("dotenv", "python-dotenv"), ("pytest", "pytest")):
        if importlib.util.find_spec(mod):
            say("OK", f"Đã cài {label}")
        else:
            say("LỖI", f"Chưa cài {label}. Chạy: python -m pip install -r requirements.txt")

    say("OK" if shutil.which("git") else "GỢI Ý", "Đã có Git" if shutil.which("git") else "Chưa có Git (tùy chọn ở mốc này; cài từ git-scm.com nếu muốn quản lý phiên bản).")

    say("THÔNG TIN", "File .env: " + ("có (không đọc nội dung)" if (ROOT / ".env").exists() else "chưa có (bình thường ở mốc M0)"))

    for rel in ("requirements.txt", ".env.example", ".gitignore", "README.md", "config/default.yaml", "src/travel/config.py"):
        if not (ROOT / rel).exists():
            say("LỖI", f"Thiếu file: {rel}")

    summary = f"Tổng kết: {counts['OK']} OK, {counts['CẢNH BÁO']} cảnh báo, {counts['LỖI']} lỗi."
    print(summary)
    lines.append(summary)
    try:
        (ROOT / "logs").mkdir(exist_ok=True)
        (ROOT / "logs" / "env_report.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("Đã lưu báo cáo: logs\\env_report.txt")
    except Exception as e:
        print(f"Không lưu được báo cáo: {e}")
    return 1 if counts["LỖI"] else 0


if __name__ == "__main__":
    sys.exit(main())
