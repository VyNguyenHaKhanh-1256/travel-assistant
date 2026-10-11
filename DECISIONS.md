# Quyết định thiết kế đã chốt (rà soát cuối trước khi code)

**LLM**
- Chính: Gemini free tier, CHỈ dùng khi qua cổng G-LLM (chưa xác minh khả dụng/quota). Không bật billing.
- Dự phòng 1: Ollama cục bộ (sau smoke test + đo độ trễ).
- Dự phòng cuối: chế độ `scripted` (code gọi tool theo intent). Khi dùng chế độ này, không tuyên bố "Agent chọn tool".
- OFF/ON ở Thí nghiệm B dùng cùng một backend. `llm_enabled=false` mặc định.

**Embedding**: ban đầu `paraphrase-multilingual-MiniLM-L12-v2` (hỗ trợ tiếng Việt: CHƯA XÁC MINH). Đối chứng `all-MiniLM-L6-v2`; `bge-m3` chỉ thử nếu mô hình chính không qua cổng. Tốc độ/RAM: chưa đo.

**Di chuyển**: bỏ OSRM khỏi MVP; chỉ Haversine, nhãn `haversine_estimate`. Chỉ là ước tính.

**Phạm vi MVP**: 2 intent (`recommend`, `itinerary`); 3 tool (`search_pois`, `get_weather`, `get_route`); Semantic Cache có khóa cứng + Temporal Guard + TTL; benchmark A (V0, V3, V4), B, C1, C2.

**Ngày hỗ trợ**: chỉ "hôm nay", "ngày mai", "ngày kia", dd/mm(/yyyy). Còn lại → `time_unresolved` → MISS.

**Quy mô**: POI tối thiểu 40 (mục tiêu 50, ≥12 trong nhà); test tối thiểu 60 (mục tiêu 80), seed 15–20; N của Thí nghiệm B: sàn 20, mục tiêu 30.

Phân loại từng giá trị (cố định / khởi tạo / phải đo): xem nhãn trong `config/default.yaml` và file Excel `MVP_Quyet_dinh_va_Checklist.xlsx`.
