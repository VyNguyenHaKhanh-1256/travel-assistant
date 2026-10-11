# PROJECT_STATE

**Mốc hiện tại:** M0 — khung dự án (chưa có ứng dụng, chưa gọi bất kỳ dịch vụ ngoài nào).
**Cập nhật:** 10/10/2026.

## Cấu trúc hiện tại
```
smart-travel/
  README.md  DECISIONS.md  PROJECT_STATE.md
  requirements.txt  .env.example  .gitignore  pytest.ini
  config/default.yaml
  data/.gitkeep
  scripts/check_env.py
  src/travel/__init__.py  src/travel/config.py
  tests/test_smoke.py
```

## File đã tạo và vai trò
| File | Vai trò |
|---|---|
| `requirements.txt` | Chỉ 3 gói: PyYAML, python-dotenv, pytest. Các gói nặng (sentence-transformers, chromadb, streamlit...) chưa cài. |
| `.env.example` | Mẫu cho khóa `GEMINI_API_KEY` (để trống). File `.env` thật không được commit. |
| `.gitignore` | Chặn `.env`, `.venv/`, `logs/`, `chroma_db/`, cache. Đã kiểm tra bằng `git check-ignore`. |
| `config/default.yaml` | Tham số mặc định, mỗi giá trị có nhãn cố định / khởi tạo / phải đo. `llm_enabled: false`. |
| `src/travel/config.py` | Đọc và kiểm tra cấu hình; đọc khóa API (không in khóa). |
| `scripts/check_env.py` | Kiểm tra máy (Python, 64-bit, venv, RAM, ổ đĩa, đường dẫn, thư viện, Git); lưu `logs\env_report.txt`. |
| `tests/test_smoke.py` | 11 kiểm thử không cần API key/mạng. |
| `DECISIONS.md` | Tóm tắt quyết định đã chốt. |

## Cách chạy (Windows, Command Prompt)
```
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python scripts\check_env.py
python -m pytest
```

## Kết quả kiểm thử
| Nơi chạy | Kết quả |
|---|---|
| Linux (môi trường của trợ lý), Python 3.12.3, PyYAML 6.0.3, python-dotenv 1.2.4, pytest 9.1.1 | `11 passed`; `check_env.py`: 9 OK, 1 cảnh báo (RAM 3.9 GB của sandbox, không phải máy của bạn), 0 lỗi. |
| **Windows của người dùng** | **CHƯA CHẠY — chờ bạn gửi kết quả `check_env.py` và `pytest`.** |

Đã xác minh thêm trong môi trường Linux: `.gitignore` bỏ qua đúng `.env`, `.venv/`, `logs/`, `chroma_db/` (bằng Git thật).

## Lỗi / rủi ro còn tồn tại
- Mã chưa được chạy trên Windows. Phần đọc RAM bằng `ctypes` (Windows) chưa được thử; nếu lỗi, script báo "Không đọc được RAM" thay vì dừng.
- Tương thích Python 3.13 trở lên với thư viện ở mốc sau (embedding, ChromaDB): CHƯA XÁC MINH. Khuyến nghị 3.11 hoặc 3.12.
- Mọi mục CHƯA XÁC MINH trong sheet `Dịch_vụ_điều_khoản` vẫn còn nguyên: quota/điều khoản Gemini, tiếng Việt của embedding, giấy phép model...
- Chưa đo RAM/tốc độ embedding trên máy của bạn.

## Bước tiếp theo
1. Bạn chạy 5 lệnh ở trên trên Windows và gửi lại: nội dung `logs\env_report.txt` và dòng cuối của `pytest`.
2. Sau khi M0-bước-môi-trường xong: cài `sentence-transformers`, tải model embedding và thử 20–30 cặp câu tiếng Việt có nhãn (M0, bước embedding).
3. Song song, làm cổng G-LLM bằng tay (không cần code): xem nhóm "Cổng G-LLM" trong sheet `Checklist`.
