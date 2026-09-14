from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "src"))

from src.clean_data import clean_data
from src.statistics import (
    calculate_statistics,
    statistics_by_blocks,
    statistics_by_province,
    rank_by_blocks,
)
from src.visualization import create_charts
from src.prediction import train_and_evaluate

CLEAN_FILE = BASE_DIR / "output" / "diem_thi_clean.csv"

# Kiểm tra và tự tạo dữ liệu sạch nếu chưa có.
def ensure_clean_data():
    if not CLEAN_FILE.exists():
        print("\n[1] Chưa có dữ liệu sạch -> đang làm sạch dữ liệu...")
        clean_data()
        print("Hoàn tất.")

    # Hiển thị thống kê tổng hợp theo từng môn.
def show_subject_statistics():
    ensure_clean_data()
    result = calculate_statistics()
    print("\n===== THỐNG KÊ THEO MÔN =====")
    print(result.to_string(index=False))

# Hiển thị số lượng và điểm trung bình theo khối thi.
def show_block_statistics():
    ensure_clean_data()
    result = statistics_by_blocks()
    print("\n===== THỐNG KÊ THEO KHỐI THI =====")
    print(result.to_string(index=False))

# Hiển thị bảng so sánh điểm giữa các tỉnh.
def show_province_statistics():
    ensure_clean_data()
    result = statistics_by_province()
    print("\n===== SO SÁNH ĐIỂM THEO TỈNH =====")
    print(result.to_string(index=False))

# Hiển thị top 10 thí sinh của từng khối thi.
def show_block_rankings():
    ensure_clean_data()
    print("\n===== XẾP HẠNG TOP 10 THEO KHỐI THI =====")
    for block, result in rank_by_blocks().items():
        print(f"\n--- KHỐI {block} ---")
        print(result.to_string(index=False))

    # Tạo biểu đồ và cho phép người dùng chọn đường dẫn biểu đồ.
def show_charts():
    ensure_clean_data()
    print("\n[Đang tạo hệ thống biểu đồ trực quan thống kê...]")
    paths = create_charts()
    names = [
        "Điểm trung bình theo môn",
        "Phân bố điểm Toán",
        "Số thí sinh theo tỉnh",
        "Ma trận tương quan giữa các môn",
        "Số lượng thí sinh theo khối",
        "Điểm trung bình theo khối",
        "Số lượng điểm 10 theo môn",
        "Số bài thi có điểm <= 1 theo môn",
        "Xếp hạng top 10 thí sinh theo khối",
        "So sánh điểm Toán trung bình theo tỉnh",
    ]

    print(f"\n===== ĐÃ TẠO VÀ LƯU {len(paths)} BIỂU ĐỒ =====")
    for number, path in enumerate(paths, 1):
        title = names[number - 1] if number <= len(names) else path
        print(f"{number}. {title}")
    print(f"{len(paths) + 1}. Xem tất cả biểu đồ")
    print("0. Quay lại menu chính")

    while True:
        choice = input(
            f"\nChọn biểu đồ (1-{len(paths)}), {len(paths) + 1} để xem tất cả, 0 để quay lại: "
        ).strip()
        if choice == "0":
            break
        if choice == str(len(paths) + 1):
            for path in paths:
                print(f"- {path}")
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(paths):
            print(f"Đường dẫn biểu đồ: {paths[int(choice) - 1]}")
        else:
            print("Lựa chọn không hợp lệ.")

# Huấn luyện và hiển thị kết quả mô hình dự đoán điểm Toán.
def run_prediction():
    ensure_clean_data()
    print("\n===== DỰ ĐOÁN ĐIỂM TOÁN =====")
    print("Mô hình học từ các môn khác. Bỏ trống môn không có điểm.")
    try:
        _, metrics = train_and_evaluate()
        print("\nĐánh giá mô hình:")
        for k, v in metrics.items():
            print(f"- {k}: {v}")
        print("\nLưu ý: đây là mô hình minh họa, không phải công cụ dự báo chính thức.")
    except Exception as e:
        print(f"Lỗi mô hình: {e}")

# Hiển thị menu chính và điều khiển toàn bộ ứng dụng.
def main():
    while True:
        print("\n" + "=" * 60)
        print("  ỨNG DỤNG XỬ LÝ VÀ PHÂN TÍCH DỮ LIỆU ĐIỂM THI THPT 2026")
        print("=" * 60)
        print("1. Làm sạch dữ liệu và tạo báo cáo")
        print("2. Thống kê điểm theo từng môn")
        print("3. Thống kê số lượng và điểm trung bình theo khối thi")
        print("4. So sánh điểm theo tỉnh")
        print("5. Xếp hạng thí sinh theo khối thi")
        print("6. Tạo và lưu các biểu đồ phân tích")
        print("7. Dự đoán điểm Toán bằng mô hình học máy")
        print("8. Chạy toàn bộ tiến trình")
        print("0. Thoát")

        choice = input("Chọn chức năng (0-8): ").strip()

        try:
            if choice == "1":
                _, report = clean_data()
                print("\n" + report)
            elif choice == "2":
                show_subject_statistics()
            elif choice == "3":
                show_block_statistics()
            elif choice == "4":
                show_province_statistics()
            elif choice == "5":
                show_block_rankings()
            elif choice == "6":
                show_charts()
            elif choice == "7":
                run_prediction()
            elif choice == "8":
                clean_data()
                show_subject_statistics()
                show_block_statistics()
                show_province_statistics()
                show_block_rankings()
                show_charts()
                run_prediction()
            elif choice == "0":
                print("Đã thoát chương trình.")
                break
            else:
                print("Lựa chọn không hợp lệ, vui lòng thử lại.")
        except FileNotFoundError as e:
            print(f"Không tìm thấy file, hãy chạy bước Làm sạch (1) trước: {e}")
        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")

if __name__ == "__main__":
    main()