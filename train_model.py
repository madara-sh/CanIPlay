"""
train_model.py
Обучает модель предсказания FPS на данных из fps_data.csv
и сохраняет её в fps_model.pkl вместе со вспомогательными данными.

Запуск:  python train_model.py
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score

DATA = "fps_data.csv"
MODEL_OUT = "fps_model.pkl"

SETTINGS_ORDER = {"low": 0, "medium": 1, "high": 2, "ultra": 3}
FEATURES = ["perf_1080", "perf_1440", "perf_4k", "vram", "year",
            "res_pixels", "settings_num", "game_code"]


def main():
    df = pd.read_csv(DATA)
    print(f"Загружено строк: {len(df)}")

    # настройки 
    df["settings_num"] = df["settings"].map(SETTINGS_ORDER)

    # игры 
    df["game"] = df["game"].astype("category")
    game_to_code = dict(enumerate(df["game"].cat.categories))   
    name_to_code = {v: k for k, v in game_to_code.items()}       
    df["game_code"] = df["game"].cat.codes

    df = df.dropna(subset=["perf_1080", "vram"])

    X = df[FEATURES]
    y = df["fps"]

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)

    model = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.1, random_state=42)
    model.fit(X_tr, y_tr)

    pred = model.predict(X_te)
    print(f"Средняя ошибка (MAE): {mean_absolute_error(y_te, pred):.1f} FPS")
    print(f"R2: {r2_score(y_te, pred):.3f}")

    # сохраняем модель 
    bundle = {
        "model": model,
        "features": FEATURES,
        "settings_order": SETTINGS_ORDER,
        "name_to_code": name_to_code,   # имя игры 
        "games": sorted(name_to_code.keys()),
    }
    joblib.dump(bundle, MODEL_OUT)
    print(f"Модель сохранена в {MODEL_OUT}")
    print(f"Игр в модели: {len(name_to_code)}")


if __name__ == "__main__":
    main()
