"""
Dashboard - Phân tích dữ liệu Điểm thi THPT 2026
Chạy: streamlit run dashboard.py
"""

from pathlib import Path
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

BASE_DIR   = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
CHART_DIR  = OUTPUT_DIR / "charts"
CLEAN_FILE = OUTPUT_DIR / "diem_thi_clean.csv"
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(
    page_title="THPT 2026 · Phân tích Điểm thi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS tối giản ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #1E40AF 0%, #2563EB 60%, #3B82F6 100%);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute;
    right: -30px; top: -40px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,.06);
    border-radius: 50%;
}
.hero h1 { margin: 0 0 6px; font-size: 1.75rem; font-weight: 800; letter-spacing: -.5px; }
.hero p  { margin: 0; opacity: .85; font-size: .95rem; }
.hero-meta { margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap; }
.badge {
    background: rgba(255,255,255,.2);
    border: 1px solid rgba(255,255,255,.3);
    border-radius: 20px;
    padding: 3px 13px;
    font-size: .78rem;
    font-weight: 600;
}

/* Section header */
.sec-header {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 16px;
    background: #EFF6FF;
    border-left: 4px solid #2563EB;
    border-radius: 0 10px 10px 0;
    margin: 20px 0 14px;
    font-weight: 700; font-size: 1rem; color: #1E40AF;
}

/* Info card */
.info-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 14px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
}
.info-card h4 { margin: 0 0 10px; color: #1E293B; font-size: .95rem; }

/* Feature grid */
.feat-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: box-shadow .2s, border-color .2s;
}
.feat-card:hover {
    box-shadow: 0 4px 16px rgba(37,99,235,.12);
    border-color: #93C5FD;
}
.feat-icon { font-size: 1.4rem; margin-bottom: 6px; }
.feat-title { font-weight: 700; font-size: .93rem; color: #1E293B; margin-bottom: 3px; }
.feat-desc  { font-size: .82rem; color: #64748B; line-height: 1.5; }

/* File status table */
.ftable { width: 100%; border-collapse: collapse; font-size: .87rem; }
.ftable th {
    background: #F1F5F9; color: #475569;
    padding: 9px 14px; text-align: left;
    font-size: .75rem; text-transform: uppercase; letter-spacing: .4px;
}
.ftable td { padding: 9px 14px; border-top: 1px solid #F1F5F9; color: #334155; }
.ftable tr:hover td { background: #F8FAFC; }

/* Block metric card */
.block-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 18px 14px;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
    transition: box-shadow .2s;
}
.block-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.1); }
.block-card .bk-name { font-size: .72rem; color: #64748B; text-transform: uppercase; letter-spacing: .5px; font-weight: 600; }
.block-card .bk-score { font-size: 2rem; font-weight: 800; margin: 4px 0; }
.block-card .bk-count { font-size: .78rem; color: #94A3B8; }
.block-card .bk-subj  { font-size: .72rem; color: #CBD5E1; margin-top: 4px; }

/* Chart wrapper */
.chart-wrap {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 16px 14px 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
    margin-bottom: 14px;
}
.chart-wrap h5 {
    margin: 0 0 10px;
    font-size: .88rem;
    font-weight: 700;
    color: #334155;
}
</style>
""", unsafe_allow_html=True)

# ── Matplotlib style ──
PALETTE  = ["#2563EB","#16A34A","#D97706","#DC2626","#7C3AED","#0891B2","#059669","#EA580C"]
BG_FIG   = "#FFFFFF"
BG_AX    = "#FAFAFA"
GRID_CLR = "#E2E8F0"
TEXT_CLR = "#334155"

def fig_style(fig, axes):
    fig.patch.set_facecolor(BG_FIG)
    for ax in (axes if isinstance(axes, (list, tuple)) else [axes]):
        ax.set_facecolor(BG_AX)
        ax.tick_params(colors=TEXT_CLR, labelsize=9)
        ax.xaxis.label.set_color(TEXT_CLR)
        ax.yaxis.label.set_color(TEXT_CLR)
        ax.title.set_color("#1E293B")
        ax.title.set_fontweight("700")
        for sp in ax.spines.values():
            sp.set_edgecolor(GRID_CLR)
        ax.grid(color=GRID_CLR, linestyle="--", linewidth=.7, alpha=.9)

def section(icon, title):
    st.markdown(f'<div class="sec-header"><span>{icon}</span><span>{title}</span></div>',
                unsafe_allow_html=True)

def check_clean_file():
    if not CLEAN_FILE.exists():
        st.error("⚠️ Chưa có dữ liệu sạch — hãy chạy **🧹 Làm sạch dữ liệu** trước!")
        return False
    return True

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 📊 THPT 2026")
    st.caption("Dashboard phân tích điểm thi")
    st.divider()

    PAGES = {
        "🏠  Tổng quan":                  "home",
        "🧹  Làm sạch dữ liệu":          "clean",
        "📈  Thống kê theo môn":          "subject_stats",
        "🎯  Thống kê theo khối thi":     "block_stats",
        "🗺   So sánh điểm theo tỉnh":    "province_stats",
        "🏆  Xếp hạng thí sinh":          "ranking",
        "🖼   Biểu đồ phân tích":         "charts",
        "🤖  Dự đoán điểm Toán (ML)":    "prediction",
    }
    page = PAGES[st.radio("Chọn trang", list(PAGES.keys()), label_visibility="collapsed")]

    st.divider()
    st.markdown("**📁 Trạng thái file**")
    files_check = {
        "Raw CSV":      BASE_DIR / "input" / "diem_thi_THPTQG_2026.csv",
        "Dữ liệu sạch": CLEAN_FILE,
        "Thống kê":     OUTPUT_DIR / "statistics_summary.csv",
        f"Charts ({len(list(CHART_DIR.glob('*.png'))) if CHART_DIR.exists() else 0})": CHART_DIR,
    }
    for name, path in files_check.items():
        icon = "🟢" if path.exists() else "🔴"
        st.caption(f"{icon}  {name}")

# ═══════════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════════
if page == "home":
    st.markdown("""
    <div class="hero">
      <h1>📊 Phân tích Điểm thi THPT Quốc gia 2026</h1>
      <p>Dashboard tương tác toàn diện — 1,131,975 thí sinh · 63 tỉnh · 10 môn thi</p>
      <div class="hero-meta">
        <span class="badge">📊 10 Biểu đồ</span>
        <span class="badge">🤖 ML Prediction</span>
        <span class="badge">📋 4 Bộ thống kê</span>
        <span class="badge">🗺 63 Tỉnh thành</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Tổng thí sinh", "1,131,975")
    c2.metric("🏫 Tỉnh / Thành phố", "63")
    c3.metric("📚 Môn thi", "10")
    c4.metric("📊 Biểu đồ", "10")

    st.markdown("")
    col_l, col_r = st.columns([1.1, 1], gap="large")

    with col_l:
        section("🛠", "Các chức năng")
        features = [
            ("🧹", "Làm sạch dữ liệu",     "Chuẩn hóa SBD, loại NaN/trùng, tạo báo cáo"),
            ("📈", "Thống kê theo môn",     "Điểm TB · Trung vị · Tỷ lệ đạt ≥5 và ≥8"),
            ("🎯", "Thống kê theo khối",    "A00, A01, B00, C00, D01 — số TS & điểm tổng"),
            ("🗺", "So sánh theo tỉnh",     "Xếp hạng 63 tỉnh theo số TS và điểm TB"),
            ("🏆", "Xếp hạng thí sinh",     "Top N thí sinh điểm cao theo từng khối"),
            ("🖼", "10 Biểu đồ phân tích",  "Cột · Histogram · Heatmap · Line · Ngang"),
            ("🤖", "Dự đoán Toán (ML)",     "Random Forest · MAE · RMSE · R²"),
        ]
        for icon, title, desc in features:
            st.markdown(f"""
            <div class="feat-card">
              <div class="feat-icon">{icon}</div>
              <div class="feat-title">{title}</div>
              <div class="feat-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    with col_r:
        section("📂", "Trạng thái file")
        file_rows = [
            ("input/diem_thi_THPTQG_2026.csv",   BASE_DIR/"input"/"diem_thi_THPTQG_2026.csv"),
            ("output/diem_thi_clean.csv",          CLEAN_FILE),
            ("output/statistics_summary.csv",      OUTPUT_DIR/"statistics_summary.csv"),
            ("output/statistics_by_province.csv",  OUTPUT_DIR/"statistics_by_province.csv"),
            ("output/cleaning_report.csv",         OUTPUT_DIR/"cleaning_report.csv"),
            ("output/charts/",                     CHART_DIR),
        ]
        rows_html = ""
        for name, path in file_rows:
            ok   = path.exists()
            icon = "✅" if ok else "❌"
            size = ""
            if ok and path.is_file():
                mb = path.stat().st_size / 1_048_576
                size = f"{mb:.1f} MB"
            rows_html += f"""<tr>
                <td style="width:28px">{icon}</td>
                <td><code style="font-size:.8rem">{name}</code></td>
                <td style="color:#94A3B8;font-size:.8rem">{size}</td>
            </tr>"""

        st.markdown(f"""
        <div class="info-card" style="padding:0;overflow:hidden">
          <table class="ftable">
            <thead><tr><th></th><th>File</th><th>Kích thước</th></tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        </div>""", unsafe_allow_html=True)

        section("🚀", "Bắt đầu nhanh")
        st.markdown("""
        <div class="info-card">
          <ol style="margin:0;padding-left:18px;color:#475569;line-height:2.1;font-size:.88rem">
            <li>Chọn <strong>🧹 Làm sạch dữ liệu</strong> nếu chưa có file sạch</li>
            <li>Duyệt qua các trang thống kê</li>
            <li>Xem <strong>🖼 Biểu đồ</strong> để hình dung trực quan</li>
            <li>Chạy <strong>🤖 Dự đoán ML</strong> để xem mô hình AI</li>
          </ol>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# LÀM SẠCH
# ═══════════════════════════════════════════════════════════════════════════
elif page == "clean":
    st.markdown("""
    <div class="hero">
      <h1>🧹 Làm sạch & Tiền xử lý dữ liệu</h1>
      <p>Chuẩn hóa SBD · Xử lý giá trị ngoài khoảng · Loại bỏ trùng lặp</p>
    </div>""", unsafe_allow_html=True)

    report_file = OUTPUT_DIR / "cleaning_report.csv"

    col_act, col_info = st.columns([1, 2.2], gap="large")
    with col_act:
        st.markdown('<div class="info-card"><h4>⚙️ Hành động</h4>', unsafe_allow_html=True)
        run_clean = st.button("▶ Chạy làm sạch dữ liệu", type="primary", use_container_width=True)
        if CLEAN_FILE.exists():
            sz = CLEAN_FILE.stat().st_size / 1_048_576
            st.success(f"✅ File sạch: {sz:.1f} MB")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_info:
        st.markdown("""
        <div class="info-card">
          <h4>📋 Các bước xử lý</h4>
          <ul style="margin:0;padding-left:18px;color:#475569;line-height:2;font-size:.88rem">
            <li>Chuẩn hóa tên tỉnh & mã SBD (zfill 8 ký tự)</li>
            <li>Chuyển điểm sang số, đặt NaN nếu ngoài [0, 10]</li>
            <li>Xóa dòng thiếu SBD hoặc Tỉnh</li>
            <li>Loại bỏ bản ghi SBD trùng (giữ lần đầu)</li>
            <li>Xóa cột toàn bộ NaN (ví dụ: Công nghệ)</li>
          </ul>
        </div>""", unsafe_allow_html=True)

    if run_clean:
        with st.spinner("Đang làm sạch dữ liệu... (1–2 phút)"):
            try:
                from src.clean_data import clean_data
                clean_data()
                st.success("✅ Hoàn tất làm sạch!")
            except Exception as e:
                st.error(f"Lỗi: {e}")

    if report_file.exists():
        section("📊", "Báo cáo làm sạch")
        report_text = report_file.read_text(encoding="utf-8")
        lines = report_text.strip().splitlines()

        key_map = {
            "Số dòng ban đầu":      ("📋", "Dòng ban đầu"),
            "Số dòng sau làm sạch": ("✅", "Sau sạch"),
            "Dòng trùng ban đầu":   ("🔁", "Dòng trùng"),
            "SBD trùng ban đầu":    ("🔂", "SBD trùng"),
        }
        metrics_raw = {}
        for line in lines:
            for key, (ico, label) in key_map.items():
                if line.startswith(key + ":"):
                    metrics_raw[label] = (ico, line.split(":", 1)[1].strip())

        if metrics_raw:
            cols = st.columns(len(metrics_raw))
            for col, (label, (ico, val)) in zip(cols, metrics_raw.items()):
                col.metric(f"{ico} {label}", val)

        missing_data, in_m = [], False
        for line in lines:
            if "Số lượng thiếu dữ liệu" in line:
                in_m = True; continue
            if in_m and line.startswith("- "):
                parts = line[2:].split(":")
                if len(parts) == 2:
                    missing_data.append({"Môn / Cột": parts[0].strip(), "Số dòng thiếu": parts[1].strip()})

        if missing_data:
            st.markdown("")
            col_t, col_c = st.columns(2, gap="large")
            with col_t:
                section("📉", "Dữ liệu thiếu sau làm sạch")
                st.dataframe(pd.DataFrame(missing_data), use_container_width=True, hide_index=True)
            with col_c:
                section("📊", "Biểu đồ dữ liệu thiếu")
                df_miss = pd.DataFrame(missing_data)
                df_miss = df_miss[df_miss["Môn / Cột"] != "SBD"].copy()
                df_miss["Số dòng thiếu"] = df_miss["Số dòng thiếu"].str.replace(",","").astype(int)
                df_miss = df_miss[df_miss["Số dòng thiếu"] > 0].sort_values("Số dòng thiếu")

                fig, ax = plt.subplots(figsize=(6.5, max(3, len(df_miss) * 0.42)))
                clrs = [PALETTE[i % len(PALETTE)] for i in range(len(df_miss))]
                bars = ax.barh(df_miss["Môn / Cột"], df_miss["Số dòng thiếu"],
                               color=clrs, edgecolor="none", height=0.6)
                fig_style(fig, ax)
                ax.set_xlabel("Số dòng thiếu")
                ax.set_title("Giá trị thiếu theo môn", pad=10)
                ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x):,}"))
                for bar in bars:
                    ax.text(bar.get_width() + max(df_miss["Số dòng thiếu"])*0.01,
                            bar.get_y() + bar.get_height()/2,
                            f"{int(bar.get_width()):,}", va="center",
                            color=TEXT_CLR, fontsize=8)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# THỐNG KÊ THEO MÔN
# ═══════════════════════════════════════════════════════════════════════════
elif page == "subject_stats":
    st.markdown("""
    <div class="hero">
      <h1>📈 Thống kê điểm theo từng môn</h1>
      <p>Điểm trung bình · Trung vị · Cao nhất · Thấp nhất · Tỷ lệ đạt</p>
    </div>""", unsafe_allow_html=True)

    cached_csv = OUTPUT_DIR / "statistics_summary.csv"
    col1, col2 = st.columns([1.4, 3])
    with col1:
        src = st.radio("Nguồn dữ liệu", ["Dùng kết quả đã lưu", "Tính lại từ đầu"])
        run_btn = st.button("▶ Hiển thị thống kê", type="primary", use_container_width=True)

    if run_btn:
        if src == "Dùng kết quả đã lưu" and cached_csv.exists():
            df = pd.read_csv(cached_csv)
        else:
            if not check_clean_file(): st.stop()
            with st.spinner("Đang tính..."):
                try:
                    from src.statistics import calculate_statistics
                    df = calculate_statistics()
                except Exception as e:
                    st.error(f"Lỗi: {e}"); st.stop()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🥇 Điểm TB cao nhất",   f"{df.iloc[0]['Môn']}", f"{df.iloc[0]['Điểm TB']:.3f} đ")
        c2.metric("📉 Điểm TB thấp nhất",  f"{df.iloc[-1]['Môn']}", f"{df.iloc[-1]['Điểm TB']:.3f} đ")
        c3.metric("✅ TB tỷ lệ đạt ≥ 5",   f"{df['Tỷ lệ >= 5 (%)'].mean():.1f}%")
        c4.metric("⭐ TB tỷ lệ đạt ≥ 8",   f"{df['Tỷ lệ >= 8 (%)'].mean():.1f}%")

        st.markdown("")
        col_t, col_c = st.columns([1, 1.5], gap="large")
        with col_t:
            section("📋", "Bảng tổng hợp")
            st.dataframe(
                df.style
                  .format({"Điểm TB":"{:.3f}","Trung vị":"{:.3f}","Cao nhất":"{:.1f}",
                            "Thấp nhất":"{:.1f}","Tỷ lệ >= 5 (%)":"{:.2f}%",
                            "Tỷ lệ >= 8 (%)":"{:.2f}%","Số bài thi":"{:,.0f}"})
                  .background_gradient(subset=["Điểm TB"], cmap="Blues"),
                use_container_width=True, hide_index=True,
            )

        with col_c:
            section("📊", "Điểm trung bình theo môn")
            fig, ax = plt.subplots(figsize=(7.5, 4.2))
            clrs = [PALETTE[0] if v >= 5 else PALETTE[3] for v in df["Điểm TB"]]
            bars = ax.bar(df["Môn"], df["Điểm TB"], color=clrs, edgecolor="none", width=0.6)
            ax.axhline(5, color=PALETTE[2], linestyle="--", linewidth=1.5,
                       label="Ngưỡng đạt (5.0)", alpha=.9)
            ax.axhline(df["Điểm TB"].mean(), color="#9333EA", linestyle=":",
                       linewidth=1.2, label=f"Trung bình ({df['Điểm TB'].mean():.2f})", alpha=.9)
            fig_style(fig, ax)
            ax.set_ylim(0, 10.5)
            for bar in bars:
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+.12,
                        f"{bar.get_height():.2f}", ha="center", fontsize=8.5,
                        color=TEXT_CLR, fontweight="600")
            plt.xticks(rotation=28, ha="right")
            ax.legend(fontsize=8, framealpha=.6)
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

        section("📊", "Tỷ lệ đạt ≥ 5 và ≥ 8 theo môn (%)")
        fig2, ax2 = plt.subplots(figsize=(11, 4))
        x, w = range(len(df)), .36
        b1 = ax2.bar([i-w/2 for i in x], df["Tỷ lệ >= 5 (%)"], w,
                     label="≥ 5 đ", color=PALETTE[0], edgecolor="none")
        b2 = ax2.bar([i+w/2 for i in x], df["Tỷ lệ >= 8 (%)"], w,
                     label="≥ 8 đ", color=PALETTE[1], edgecolor="none")
        fig_style(fig2, ax2)
        ax2.set_xticks(list(x)); ax2.set_xticklabels(df["Môn"], rotation=25, ha="right")
        ax2.set_ylabel("Tỷ lệ (%)"); ax2.legend(fontsize=9)
        for bar in list(b1)+list(b2):
            ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+.5,
                     f"{bar.get_height():.1f}", ha="center", color=TEXT_CLR, fontsize=7.5)
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)
        plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# THỐNG KÊ THEO KHỐI
# ═══════════════════════════════════════════════════════════════════════════
elif page == "block_stats":
    st.markdown("""
    <div class="hero">
      <h1>🎯 Thống kê theo khối thi</h1>
      <p>A00 · A01 · B00 · C00 · D01 — Số thí sinh & Điểm tổng hợp</p>
    </div>""", unsafe_allow_html=True)

    run_btn = st.button("▶ Tính thống kê theo khối", type="primary")
    if run_btn:
        if not check_clean_file(): st.stop()
        with st.spinner("Đang xử lý..."):
            try:
                from src.statistics import statistics_by_blocks
                df = statistics_by_blocks()
            except Exception as e:
                st.error(f"Lỗi: {e}"); st.stop()

        BCLR  = ["#2563EB","#16A34A","#D97706","#7C3AED","#DC2626"]
        BSUBJ = {"A00":"Toán · Lý · Hóa","A01":"Toán · Lý · Ngoại ngữ",
                 "B00":"Toán · Hóa · Sinh","C00":"Văn · Sử · Địa","D01":"Toán · Văn · Ngoại ngữ"}

        cols = st.columns(len(df))
        for col, (_, row), clr in zip(cols, df.iterrows(), BCLR):
            col.markdown(f"""
            <div class="block-card" style="border-top:4px solid {clr}">
              <div class="bk-name">Khối {row['Khối thi']}</div>
              <div class="bk-score" style="color:{clr}">{row['Điểm TB']:.2f}</div>
              <div class="bk-count">{int(row['Số TS']):,} thí sinh</div>
              <div class="bk-subj">{BSUBJ.get(row['Khối thi'],'')}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")
        col_t, col_c = st.columns(2, gap="large")
        with col_t:
            section("📋", "Bảng chi tiết")
            st.dataframe(df.style.background_gradient(subset=["Điểm TB"], cmap="Blues"),
                         use_container_width=True, hide_index=True)
        with col_c:
            section("📊", "Biểu đồ so sánh")
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4.5))
            bnames = df["Khối thi"].tolist()
            clrs   = BCLR[:len(bnames)]

            ax1.bar(bnames, df["Số TS"], color=clrs, edgecolor="none", width=.55)
            fig_style(fig, ax1); ax1.set_title("Số lượng thí sinh")
            ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x/1000)}k"))
            for bar in ax1.patches:
                ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+500,
                         f"{int(bar.get_height()):,}", ha="center", color=TEXT_CLR, fontsize=8)

            ax2.bar(bnames, df["Điểm TB"], color=clrs, edgecolor="none", width=.55)
            fig_style(fig, ax2); ax2.set_title("Điểm TB tổng 3 môn")
            ax2.set_ylim(0, 32)
            for bar in ax2.patches:
                ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+.1,
                         f"{bar.get_height():.2f}", ha="center", color=TEXT_CLR,
                         fontsize=9, fontweight="600")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# SO SÁNH TỈNH
# ═══════════════════════════════════════════════════════════════════════════
elif page == "province_stats":
    st.markdown("""
    <div class="hero">
      <h1>🗺 So sánh điểm theo tỉnh / thành phố</h1>
      <p>Phân tích 63 tỉnh thành — Số thí sinh & Điểm trung bình các môn</p>
    </div>""", unsafe_allow_html=True)

    cached_csv = OUTPUT_DIR / "statistics_by_province.csv"
    c1, c2, c3 = st.columns([1.3, 1, 2])
    with c1: src = st.radio("Nguồn dữ liệu", ["Dùng kết quả đã lưu","Tính lại từ đầu"])
    with c2: top_n = st.slider("Hiển thị top", 10, 63, 20)
    with c3: run_btn = st.button("▶ Xem so sánh tỉnh", type="primary", use_container_width=True)

    if run_btn:
        if src == "Dùng kết quả đã lưu" and cached_csv.exists():
            df = pd.read_csv(cached_csv)
        else:
            if not check_clean_file(): st.stop()
            with st.spinner("Đang xử lý..."):
                try:
                    from src.statistics import statistics_by_province
                    df = statistics_by_province()
                except Exception as e:
                    st.error(f"Lỗi: {e}"); st.stop()

        df_show = df.head(top_n)
        base_cols = ["Tỉnh","Số thí sinh"]
        mean_cols = [c for c in df_show.columns if "Điểm TB" in c][:6]
        section("📋", f"Top {top_n} tỉnh theo số thí sinh")
        st.dataframe(df_show[base_cols+mean_cols], use_container_width=True, hide_index=True)

        col_c1, col_c2 = st.columns(2, gap="large")
        with col_c1:
            section("👥", f"Top {top_n} — Số thí sinh")
            data_plot = df_show.sort_values("Số thí sinh")
            fig, ax = plt.subplots(figsize=(6.5, max(5, top_n*.32)))
            grad = plt.cm.Blues([.35+.65*i/len(data_plot) for i in range(len(data_plot))])
            ax.barh(data_plot["Tỉnh"], data_plot["Số thí sinh"],
                    color=grad, edgecolor="none", height=.7)
            fig_style(fig, ax)
            ax.set_xlabel("Số thí sinh")
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{int(x/1000)}k"))
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

        with col_c2:
            if "Toán Điểm TB" in df.columns:
                section("📐", f"Top {top_n} — Điểm Toán TB")
                df_t = df.dropna(subset=["Toán Điểm TB"]).nlargest(top_n,"Toán Điểm TB").sort_values("Toán Điểm TB")
                grad2 = plt.cm.Purples([.35+.65*i/len(df_t) for i in range(len(df_t))])
                fig2, ax2 = plt.subplots(figsize=(6.5, max(5, top_n*.32)))
                ax2.barh(df_t["Tỉnh"], df_t["Toán Điểm TB"], color=grad2, edgecolor="none", height=.7)
                fig_style(fig2, ax2)
                ax2.set_xlabel("Điểm Toán TB")
                for bar in ax2.patches:
                    ax2.text(bar.get_width()+.02, bar.get_y()+bar.get_height()/2,
                             f"{bar.get_width():.2f}", va="center", color=TEXT_CLR, fontsize=7.5)
                plt.tight_layout()
                st.pyplot(fig2, use_container_width=True)
                plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# XẾP HẠNG
# ═══════════════════════════════════════════════════════════════════════════
elif page == "ranking":
    st.markdown("""
    <div class="hero">
      <h1>🏆 Xếp hạng Top thí sinh theo khối thi</h1>
      <p>Tìm ra những thí sinh xuất sắc nhất theo tổng điểm từng khối</p>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 3])
    with c1:
        top_n = st.slider("Số thí sinh top", 5, 30, 10)
        run_btn = st.button("▶ Xem xếp hạng", type="primary", use_container_width=True)

    if run_btn:
        if not check_clean_file(): st.stop()
        with st.spinner("Đang xếp hạng..."):
            try:
                from src.statistics import rank_by_blocks
                rankings = rank_by_blocks(limit=top_n)
            except Exception as e:
                st.error(f"Lỗi: {e}"); st.stop()

        BSUBJ = {"A00":["Toán","Lý","Hóa"],"A01":["Toán","Lý","Ngoại ngữ"],
                 "B00":["Toán","Hóa","Sinh"],"C00":["Văn","Sử","Địa"],"D01":["Toán","Văn","Ngoại ngữ"]}
        BCLR  = {"A00":PALETTE[0],"A01":PALETTE[1],"B00":PALETTE[2],"C00":PALETTE[4],"D01":PALETTE[3]}

        tabs = st.tabs([f"  Khối {b}  " for b in rankings])
        for tab, (block, df_r) in zip(tabs, rankings.items()):
            with tab:
                clr  = BCLR.get(block, PALETTE[0])
                subj = " · ".join(BSUBJ.get(block,[]))
                st.markdown(f"""
                <div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:10px;
                            padding:10px 16px;margin-bottom:14px;display:flex;align-items:center;gap:12px">
                  <span style="background:{clr};color:white;border-radius:8px;padding:4px 14px;
                               font-weight:700;font-size:.9rem">Khối {block}</span>
                  <span style="color:#475569;font-size:.88rem">📚 {subj}</span>
                </div>""", unsafe_allow_html=True)

                col_t, col_c = st.columns([1, 1.3], gap="large")
                with col_t:
                    def row_style(row):
                        h = int(row["Hạng"])
                        if h == 1: return ["background:#FEF9C3;font-weight:700"]*len(row)
                        if h == 2: return ["background:#F1F5F9;font-weight:700"]*len(row)
                        if h == 3: return ["background:#FEF3C7;font-weight:700"]*len(row)
                        return [""]*len(row)
                    st.dataframe(df_r.style.apply(row_style, axis=1).format({"Điểm":"{:.2f}"}),
                                 use_container_width=True, hide_index=True)

                with col_c:
                    fig, ax = plt.subplots(figsize=(5.5, max(3, len(df_r)*.45)))
                    bar_clrs = [PALETTE[2] if i==0 else clr if i<3 else "#CBD5E1" for i in range(len(df_r))]
                    bars = ax.barh(
                        [f"#{r} {sbd}" for r,sbd in zip(df_r["Hạng"],df_r["SBD"])],
                        df_r["Điểm"], color=bar_clrs, edgecolor="none", height=.65,
                    )
                    ax.invert_yaxis()
                    fig_style(fig, ax)
                    ax.set_xlabel("Tổng điểm")
                    ax.set_title(f"Top {len(df_r)} — Khối {block}", pad=10)
                    for bar in bars:
                        ax.text(bar.get_width()-.1, bar.get_y()+bar.get_height()/2,
                                f"{bar.get_width():.2f}", va="center", ha="right",
                                color="white", fontsize=9, fontweight="700")
                    plt.tight_layout()
                    st.pyplot(fig, use_container_width=True)
                    plt.close()

# ═══════════════════════════════════════════════════════════════════════════
# BIỂU ĐỒ
# ═══════════════════════════════════════════════════════════════════════════
elif page == "charts":
    st.markdown("""
    <div class="hero">
      <h1>🖼 Biểu đồ phân tích dữ liệu</h1>
      <p>10 biểu đồ trực quan — Cột · Histogram · Heatmap · Line · Ngang</p>
    </div>""", unsafe_allow_html=True)

    CHART_NAMES = {
        "01_diem_trung_binh.png":             ("📊", "Điểm trung bình theo môn"),
        "02_phan_bo_diem_toan.png":           ("📉", "Phân bố điểm môn Toán"),
        "03_so_thi_sinh_theo_tinh.png":       ("🗺", "Top 20 tỉnh — Số thí sinh"),
        "04_ma_tran_tuong_quan.png":          ("🔗", "Ma trận tương quan"),
        "05_so_luong_thi_sinh_theo_khoi.png": ("🎯", "Số thí sinh theo khối"),
        "06_diem_trung_binh_cac_khoi.png":    ("📈", "Điểm TB theo khối"),
        "07_so_luong_diem_10.png":            ("🌟", "Số lượng điểm 10"),
        "08_so_bai_thi_rot.png":              ("⚠️", "Bài thi điểm ≤ 1"),
        "09_xep_hang_thi_sinh_theo_khoi.png": ("🏆", "Top 10 thí sinh theo khối"),
        "10_so_sanh_diem_theo_tinh.png":      ("🗾", "Điểm Toán TB theo tỉnh"),
    }

    c1, c2 = st.columns([1.4, 3])
    with c1:
        regen = st.button("🔄 Tạo lại toàn bộ biểu đồ", type="secondary", use_container_width=True)
    existing = sorted(CHART_DIR.glob("*.png")) if CHART_DIR.exists() else []
    with c2:
        if existing:
            st.info(f"✅ Có **{len(existing)} biểu đồ** sẵn sàng trong `output/charts/`")

    if regen:
        if not check_clean_file(): st.stop()
        with st.spinner("Đang tạo 10 biểu đồ..."):
            try:
                from src.visualization import create_charts
                paths = create_charts()
                st.success(f"✅ Đã tạo {len(paths)} biểu đồ!")
                existing = sorted(CHART_DIR.glob("*.png"))
            except Exception as e:
                st.error(f"Lỗi: {e}")

    if not existing:
        st.info("ℹ️ Chưa có biểu đồ. Nhấn **Tạo lại toàn bộ biểu đồ** để bắt đầu.")
    else:
        chart_opts = {CHART_NAMES.get(p.name, ("📊", p.name))[1]: p for p in existing}
        selected   = st.multiselect("🎨 Chọn biểu đồ xem", list(chart_opts.keys()),
                                    default=list(chart_opts.keys()))

        items = [(k, chart_opts[k]) for k in selected]
        for i in range(0, len(items), 2):
            cols = st.columns(2, gap="medium")
            for j, (name, path) in enumerate(items[i:i+2]):
                with cols[j]:
                    ico = CHART_NAMES.get(path.name, ("📊",""))[0]
                    st.markdown(f"""
                    <div class="chart-wrap">
                      <h5>{ico} {name}</h5>
                    </div>""", unsafe_allow_html=True)
                    st.image(str(path), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# DỰ ĐOÁN ML
# ═══════════════════════════════════════════════════════════════════════════
elif page == "prediction":
    st.markdown("""
    <div class="hero">
      <h1>🤖 Dự đoán điểm Toán bằng Machine Learning</h1>
      <p>Random Forest Regressor · Học từ điểm các môn khác để dự đoán điểm Toán</p>
    </div>""", unsafe_allow_html=True)

    col_info, col_act = st.columns([1.8, 1], gap="large")
    with col_info:
        st.markdown("""
        <div class="info-card">
          <h4>📐 Thông tin mô hình</h4>
          <table style="width:100%;font-size:.88rem;border-collapse:collapse">
            <tr><td style="color:#64748B;padding:6px 0;width:40%">Thuật toán</td>
                <td style="font-weight:600;color:#1E293B">Random Forest Regressor</td></tr>
            <tr style="border-top:1px solid #F1F5F9">
                <td style="color:#64748B;padding:6px 0">Biến mục tiêu</td>
                <td style="font-weight:600;color:#1E293B">Điểm Toán</td></tr>
            <tr style="border-top:1px solid #F1F5F9">
                <td style="color:#64748B;padding:6px 0">Biến đầu vào</td>
                <td style="font-weight:600;color:#1E293B">Văn, Lý, Hóa, Sinh, Sử, Địa, Ngoại ngữ...</td></tr>
            <tr style="border-top:1px solid #F1F5F9">
                <td style="color:#64748B;padding:6px 0">Chia tập</td>
                <td style="font-weight:600;color:#1E293B">80% Train · 20% Test</td></tr>
            <tr style="border-top:1px solid #F1F5F9">
                <td style="color:#64748B;padding:6px 0">Cấu hình</td>
                <td style="font-weight:600;color:#1E293B">100 cây · Max depth: 12</td></tr>
          </table>
          <div style="margin-top:14px;padding:10px 14px;background:#FFFBEB;
                      border:1px solid #FDE68A;border-radius:8px;
                      font-size:.82rem;color:#92400E">
            ⚠️ Mô hình minh họa học thuật, không phải công cụ dự báo chính thức.
          </div>
        </div>""", unsafe_allow_html=True)

    with col_act:
        st.markdown('<div class="info-card"><h4>⚙️ Tham số</h4>', unsafe_allow_html=True)
        sample_size = st.number_input("Số mẫu huấn luyện", 10_000, 200_000, 50_000, 10_000)
        run_btn = st.button("▶ Huấn luyện & Đánh giá", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if run_btn:
        if not check_clean_file(): st.stop()
        with st.spinner(f"Đang huấn luyện với {int(sample_size):,} mẫu... (1–3 phút)"):
            try:
                from src.prediction import train_and_evaluate
                model, metrics = train_and_evaluate(sample_size=int(sample_size))
                st.success("✅ Huấn luyện hoàn tất!")
            except Exception as e:
                st.error(f"Lỗi: {e}"); st.stop()

        r2   = float(metrics.get("R2", 0))
        mae  = float(metrics.get("MAE", 0))
        rmse = float(metrics.get("RMSE", 0))
        r2_label = "🟢 Tốt" if r2 > .7 else "🟡 Khá" if r2 > .5 else "🔴 Yếu"

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📏 MAE", f"{mae:.4f}", "Sai số tuyệt đối TB")
        c2.metric("📐 RMSE", f"{rmse:.4f}", "Căn sai số bình phương")
        c3.metric("🎯 R²", f"{r2:.4f}", r2_label)
        c4.metric("📦 Số mẫu", f"{int(metrics.get('Số mẫu dùng huấn luyện + kiểm tra', 0)):,}")

        st.markdown("")
        col_g, col_d = st.columns([1.5, 1], gap="large")
        with col_g:
            section("📊", "Biểu đồ đánh giá")
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.8))

            clr_r2 = PALETTE[1] if r2 > .7 else PALETTE[2] if r2 > .5 else PALETTE[3]
            ax1.barh(["R² Score"], [1],   color="#E2E8F0",  edgecolor="none", height=.45)
            ax1.barh(["R² Score"], [r2], color=clr_r2,    edgecolor="none", height=.45)
            ax1.set_xlim(0, 1)
            ax1.set_title("R² Score (0 → 1)", pad=10)
            ax1.text(r2/2, 0, f"{r2:.4f}", ha="center", va="center",
                     color="white", fontsize=13, fontweight="800")
            fig_style(fig, ax1)

            ax2.bar(["MAE","RMSE"], [mae, rmse],
                    color=[PALETTE[0], PALETTE[4]], edgecolor="none", width=.45)
            fig_style(fig, ax2)
            ax2.set_title("Sai số mô hình", pad=10)
            for bar in ax2.patches:
                ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+.002,
                         f"{bar.get_height():.4f}", ha="center",
                         color=TEXT_CLR, fontsize=11, fontweight="700")
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close()

        with col_d:
            section("📋", "Chi tiết chỉ số")
            df_m = pd.DataFrame({"Chỉ số": list(metrics.keys()),
                                  "Giá trị": list(metrics.values())})
            st.dataframe(df_m, use_container_width=True, hide_index=True, height=310)

