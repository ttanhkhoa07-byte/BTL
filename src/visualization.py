from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Trỏ ra thư mục gốc (vì file này nằm trong thư mục src/)
BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_FILE = BASE_DIR / "output" / "diem_thi_clean.csv"
CHART_DIR = BASE_DIR / "output" / "charts"

# Tạo và lưu toàn bộ biểu đồ phân tích dữ liệu điểm thi.
def create_charts(clean_file=CLEAN_FILE, chart_dir=CHART_DIR):
    df = pd.read_csv(clean_file)
    chart_dir.mkdir(parents=True, exist_ok=True)
    for old_chart in chart_dir.glob("*.png"):
        old_chart.unlink()

    score_cols = [c for c in df.columns if c not in ["SBD", "Tỉnh"]]

    # 1. Điểm trung bình theo môn
    means = df[score_cols].mean().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    bars = means.plot(kind="bar", color="steelblue", edgecolor="black")
    plt.title("Điểm trung bình theo môn", fontsize=14, fontweight="bold")
    plt.xlabel("Môn thi")
    plt.ylabel("Điểm trung bình")
    plt.xticks(rotation=45, ha="right")
    for bar in bars.patches:
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{bar.get_height():.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.tight_layout()
    plt.savefig(chart_dir / "01_diem_trung_binh.png", dpi=150)
    plt.close()

    # 2. Phân bố điểm Toán
    if "Toán" in df:
        plt.figure(figsize=(10, 6))
        df["Toán"].dropna().plot(kind="hist", bins=40, color="orange", edgecolor="black")
        plt.title("Phân bố điểm môn Toán", fontsize=14, fontweight="bold")
        plt.xlabel("Điểm")
        plt.ylabel("Số lượng thí sinh")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout()
        plt.savefig(chart_dir / "02_phan_bo_diem_toan.png", dpi=150)
        plt.close()

    # 3. Top 20 tỉnh có số lượng thí sinh nhiều nhất
    province_counts = df["Tỉnh"].value_counts().head(20)
    plt.figure(figsize=(12, 7))
    province_counts.sort_values().plot(kind="barh", color="forestgreen", edgecolor="black")
    plt.title("Top 20 tỉnh có số lượng thí sinh dự thi cao nhất", fontsize=14, fontweight="bold")
    plt.xlabel("Số thí sinh")
    plt.ylabel("Tỉnh")
    plt.tight_layout()
    plt.savefig(chart_dir / "03_so_thi_sinh_theo_tinh.png", dpi=150)
    plt.close()

    # 4. Ma trận tương quan các môn
    corr = df[score_cols].corr()
    plt.figure(figsize=(11, 8))
    plt.imshow(corr, aspect="auto", cmap="coolwarm")
    plt.colorbar(label="Hệ số tương quan")
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
    plt.yticks(range(len(corr.index)), corr.index)
    plt.title("Ma trận tương quan giữa các môn", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(chart_dir / "04_ma_tran_tuong_quan.png", dpi=150)
    plt.close()

    # 5. Số lượng thí sinh theo khối
    block_subjects = {
        "A00": ["Toán", "Lý", "Hóa"],
        "A01": ["Toán", "Lý", "Ngoại ngữ"],
        "B00": ["Toán", "Hóa", "Sinh"],
        "C00": ["Văn", "Sử", "Địa"],
        "D01": ["Toán", "Văn", "Ngoại ngữ"],
    }
    block_scores = {
        block: df[subjects].sum(axis=1, min_count=3).dropna()
        for block, subjects in block_subjects.items()
        if set(subjects).issubset(df.columns)
    }
    blocks = list(block_scores)
    counts = [len(block_scores[block]) for block in blocks]
    means_block = [block_scores[block].mean() for block in blocks]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(blocks, counts, color="skyblue", edgecolor="black")
    plt.title("Số lượng thí sinh theo khối thi", fontsize=14, fontweight="bold")
    plt.xlabel("Khối thi")
    plt.ylabel("Số thí sinh")
    for bar in bars:
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 20,
            f"{int(bar.get_height()):,}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.tight_layout()
    plt.savefig(chart_dir / "05_so_luong_thi_sinh_theo_khoi.png", dpi=150)
    plt.close()

    # 6. Điểm trung bình theo khối
    plt.figure(figsize=(10, 6))
    bars = plt.bar(blocks, means_block, color="crimson", edgecolor="black")
    plt.title("Điểm trung bình theo khối thi", fontsize=14, fontweight="bold")
    plt.xlabel("Khối thi")
    plt.ylabel("Điểm trung bình")
    for bar in bars:
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{bar.get_height():.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    plt.tight_layout()
    plt.savefig(chart_dir / "06_diem_trung_binh_cac_khoi.png", dpi=150)
    plt.close()

    # 7. Số lượng điểm 10 theo môn
    perfect_scores = {col: int((df[col] == 10.0).sum()) for col in score_cols}
    perfect_scores = {col: count for col, count in perfect_scores.items() if count > 0}
    plt.figure(figsize=(10, 5))
    bars = plt.bar(perfect_scores.keys(), perfect_scores.values(), color="gold", edgecolor="black")
    plt.title("Số lượng điểm 10 tuyệt đối theo môn", fontsize=14, fontweight="bold")
    plt.ylabel("Số lượng điểm 10")
    plt.xticks(rotation=45, ha="right")
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                 f"{int(bar.get_height()):,}", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(chart_dir / "07_so_luong_diem_10.png", dpi=150)
    plt.close()

    # 8. Số bài thi có điểm <= 1 theo môn
    low_scores = {col: int((df[col] <= 1.0).sum()) for col in score_cols}
    low_scores = {col: count for col, count in low_scores.items() if count > 0}
    plt.figure(figsize=(10, 5))
    bars = plt.bar(low_scores.keys(), low_scores.values(), color="tomato", edgecolor="black")
    plt.title("Số lượng bài thi có điểm <= 1 theo môn", fontsize=14, fontweight="bold")
    plt.ylabel("Số lượng bài thi")
    plt.xticks(rotation=45, ha="right")
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                 f"{int(bar.get_height()):,}", ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(chart_dir / "08_so_bai_thi_rot.png", dpi=150)
    plt.close()

    # 9. Xếp hạng top 10 thí sinh theo khối
    ranking_data = {}
    for block, scores in block_scores.items():
        ranking_data[block] = scores.nlargest(10).reset_index(drop=True)

    plt.figure(figsize=(11, 6))
    for block, scores in ranking_data.items():
        plt.plot(
            range(1, len(scores) + 1),
            scores,
            marker="o",
            linewidth=2,
            label=block,
        )
    plt.title("Xếp hạng top 10 thí sinh theo khối thi", fontsize=14, fontweight="bold")
    plt.xlabel("Thứ hạng")
    plt.ylabel("Tổng điểm khối")
    plt.xticks(range(1, 11))
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend(title="Khối thi")
    plt.tight_layout()
    plt.savefig(chart_dir / "09_xep_hang_thi_sinh_theo_khoi.png", dpi=150)
    plt.close()

    # 10. So sánh điểm Toán trung bình theo tỉnh
    province_scores = df.groupby("Tỉnh")["Toán"].mean().dropna()
    province_scores = province_scores.nlargest(20).sort_values()
    plt.figure(figsize=(11, 7))
    bars = plt.barh(province_scores.index, province_scores.values,
                    color="mediumpurple", edgecolor="black")
    plt.title("Top 20 tỉnh có điểm Toán trung bình cao nhất",
              fontsize=14, fontweight="bold")
    plt.xlabel("Điểm Toán trung bình")
    plt.ylabel("Tỉnh")
    for bar in bars:
        plt.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                 f"{bar.get_width():.3f}", va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(chart_dir / "10_so_sanh_diem_theo_tinh.png", dpi=150)
    plt.close()

    return sorted(str(path) for path in chart_dir.glob("*.png"))

if __name__ == "__main__":
    paths = create_charts()
    print("Đã tạo hoàn chỉnh các biểu đồ:")
    for p in paths:
        print("-", p)