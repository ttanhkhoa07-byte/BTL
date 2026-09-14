from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "input" / "diem_thi_THPTQG_2026.csv"
OUTPUT_FILE = BASE_DIR / "output" / "diem_thi_clean.csv"
REPORT_FILE = BASE_DIR / "output" / "cleaning_report.csv"

SCORE_COLUMNS = [
    "Toán", "Văn", "Lý", "Hóa", "Sinh", "Sử", "Địa",
    "GD Kinh tế - Pháp luật", "Tin học", "Công nghệ", "Ngoại ngữ"
]

# Làm sạch dữ liệu điểm và lưu dữ liệu cùng báo cáo kết quả.
def clean_data(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    df = pd.read_csv(input_file, dtype={"SBD": "string"})

    original_rows, original_cols = df.shape
    original_duplicates = int(df.duplicated().sum())
    original_sbd_duplicates = int(df["SBD"].duplicated().sum())

    # Chuẩn hóa tên tỉnh và mã số báo danh.
    df["Tỉnh"] = df["Tỉnh"].astype("string").str.strip()
    df["SBD"] = (
        df["SBD"].astype("string").str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )
    valid_sbd = df["SBD"].str.fullmatch(r"\d{1,8}")
    df.loc[~valid_sbd, "SBD"] = pd.NA
    df["SBD"] = df["SBD"].str.zfill(8)

    # Chuyển điểm sang số; giá trị không hợp lệ trở thành NaN.
    for col in SCORE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df.loc[~df[col].between(0, 10), col] = pd.NA

    # SBD và Tỉnh là thông tin bắt buộc.
    df = df.dropna(subset=["SBD", "Tỉnh"])

    # Loại bản ghi trùng.
    df = df.drop_duplicates(subset=["SBD"], keep="first")

    # Cột Công nghệ hiện không có dữ liệu nào nên loại khỏi dữ liệu phân tích.
    removed_all_null_columns = []
    for col in list(df.columns):
        if col not in ["SBD", "Tỉnh"] and df[col].isna().all():
            removed_all_null_columns.append(col)
            df = df.drop(columns=[col])

    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    report = [
        "BÁO CÁO LÀM SẠCH DỮ LIỆU",
        "=" * 60,
        f"Số dòng ban đầu: {original_rows:,}",
        f"Số cột ban đầu: {original_cols}",
        f"Số dòng sau làm sạch: {len(df):,}",
        f"Số cột sau làm sạch: {df.shape[1]}",
        f"Dòng trùng ban đầu: {original_duplicates:,}",
        f"SBD trùng ban đầu: {original_sbd_duplicates:,}",
        f"Cột toàn bộ thiếu dữ liệu đã loại: {', '.join(removed_all_null_columns) or 'Không có'}",
        "",
        "Số lượng thiếu dữ liệu sau làm sạch:",
    ]
    missing = df.isna().sum()
    for col, n in missing.items():
        report.append(f"- {col}: {int(n):,}")

    REPORT_FILE.write_text("\n".join(report), encoding="utf-8")
    return df, "\n".join(report)

if __name__ == "__main__":
    _, report = clean_data()
    print(report)
    print(f"\nĐã tạo: {OUTPUT_FILE}")