from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_FILE = BASE_DIR / "output" / "diem_thi_clean.csv"

FEATURES = [
    "Văn", "Lý", "Hóa", "Sinh", "Sử", "Địa",
    "GD Kinh tế - Pháp luật", "Tin học", "Ngoại ngữ"
]
TARGET = "Toán"

# Huấn luyện mô hình dự đoán điểm Toán và tính các chỉ số đánh giá.
def train_and_evaluate(clean_file=CLEAN_FILE, sample_size=50000, random_state=42):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    df = pd.read_csv(clean_file)
    available = [c for c in FEATURES if c in df.columns]
    data = df[[TARGET] + available].dropna(subset=[TARGET]).copy()

    usable = [c for c in available if data[c].notna().sum() >= max(100, len(data) * 0.02)]
    if not usable:
        raise ValueError("Không có đủ biến đầu vào cho mô hình dự đoán.")

    if len(data) > sample_size:
        data = data.sample(sample_size, random_state=random_state)

    X = data[usable]
    y = data[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            n_jobs=-1,
            random_state=random_state
        ))
    ])
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    metrics = {
        "Số mẫu dùng huấn luyện + kiểm tra": len(data),
        "Số biến đầu vào": len(usable),
        "Biến đầu vào": ", ".join(usable),
        "MAE": round(mean_absolute_error(y_test, pred), 4),
        "RMSE": round(np.sqrt(mean_squared_error(y_test, pred)), 4),
        "R2": round(r2_score(y_test, pred), 4),
    }
    return model, metrics

if __name__ == "__main__":
    model, metrics = train_and_evaluate()
    print("KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH")
    for k, v in metrics.items():
        print(f"{k}: {v}")