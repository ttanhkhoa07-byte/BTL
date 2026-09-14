from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_FILE = BASE_DIR / "output" / "diem_thi_clean.csv"
OUTPUT_FILE = BASE_DIR / "output" / "statistics_summary.csv"
PROVINCE_OUTPUT_FILE = BASE_DIR / "output" / "statistics_by_province.csv"

BLOCK_SUBJECTS = {
    "A00": ["Toán", "Lý", "Hóa"],
    "A01": ["Toán", "Lý", "Ngoại ngữ"],
    "B00": ["Toán", "Hóa", "Sinh"],
    "C00": ["Văn", "Sử", "Địa"],
    "D01": ["Toán", "Văn", "Ngoại ngữ"],
}

# Tính các chỉ số thống kê cơ bản cho từng môn.
def calculate_statistics(clean_file=CLEAN_FILE, output_file=OUTPUT_FILE):
    df = pd.read_csv(clean_file)

    score_cols = [c for c in df.columns if c not in ["SBD", "Tỉnh"]]
    rows = []
    
    for col in score_cols:
        s = df[col].dropna()
        if s.empty:
            continue
        rows.append({
            "Môn": col,
            "Số bài thi": int(s.size),
            "Điểm TB": round(s.mean(), 3),
            "Trung vị": round(s.median(), 3),
            "Cao nhất": round(s.max(), 3),
            "Thấp nhất": round(s.min(), 3),
            "Tỷ lệ >= 5 (%)": round((s >= 5).mean() * 100, 2),
            "Tỷ lệ >= 8 (%)": round((s >= 8).mean() * 100, 2),
        })

    result = pd.DataFrame(rows).sort_values("Điểm TB", ascending=False)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_file, index=False, encoding="utf-8-sig")
    return result

# Tính số lượng và điểm tổng hợp của từng khối thi.
def statistics_by_blocks(clean_file=CLEAN_FILE):
    df = pd.read_csv(clean_file)
    blocks = BLOCK_SUBJECTS
    block_stats = []
    for block, subjects in blocks.items():
        if not set(subjects).issubset(df.columns):
            continue
        s = df[subjects].sum(axis=1, min_count=3).dropna()
        if not s.empty:
            block_stats.append({
                "Khối thi": block,
                "Số TS": int(s.size),
                "Điểm TB": round(s.mean(), 3),
                "Cao nhất": round(s.max(), 3),
            })
    return pd.DataFrame(block_stats)

# So sánh số lượng thí sinh và điểm các môn theo tỉnh.
def statistics_by_province(clean_file=CLEAN_FILE, output_file=PROVINCE_OUTPUT_FILE):
    df = pd.read_csv(clean_file)
    score_cols = [column for column in df.columns if column not in ["SBD", "Tỉnh"]]
    result = df.groupby("Tỉnh")[score_cols].agg(["count", "mean"])
    result.columns = [
        f"{subject} {'Số bài' if metric == 'count' else 'Điểm TB'}"
        for subject, metric in result.columns
    ]
    result.insert(0, "Số thí sinh", df.groupby("Tỉnh").size())
    result = result.sort_values("Số thí sinh", ascending=False).reset_index()
    result.to_csv(output_file, index=False, encoding="utf-8-sig")
    return result

# Xếp hạng top thí sinh theo tổng điểm của từng khối.
def rank_by_blocks(clean_file=CLEAN_FILE, limit=10):
    df = pd.read_csv(clean_file, dtype={"SBD": "string"})
    rankings = {}
    for block, subjects in BLOCK_SUBJECTS.items():
        if not set(subjects).issubset(df.columns):
            continue
        scores = df[subjects].sum(axis=1, min_count=3)
        ranked = df[["SBD", "Tỉnh"]].copy()
        ranked["Điểm"] = scores
        ranked = ranked.dropna(subset=["Điểm"]).sort_values("Điểm", ascending=False).head(limit)
        ranked.insert(0, "Hạng", range(1, len(ranked) + 1))
        rankings[block] = ranked.reset_index(drop=True)
    return rankings

if __name__ == "__main__":
    print("===== THỐNG KÊ THEO MÔN =====")
    print(calculate_statistics().to_string(index=False))
    print("\n===== THỐNG KÊ THEO KHỐI =====")
    print(statistics_by_blocks().to_string(index=False))