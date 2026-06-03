import tkinter as tk
import psutil
import GPUtil
import clr
import joblib
import pandas as pd

from gpu_specs import GPU_SPECS
from rtx50_patch import RTX_50_SERIES
GPU_SPECS.update(RTX_50_SERIES)  # добавляем новые карты, которых нет в датасете

# ---------- LibreHardwareMonitor (температура CPU) ----------
dll_path = r"C:\Users\mlbeast\Downloads\LibreHardwareMonitor\LibreHardwareMonitorLib.dll"
clr.AddReference(dll_path)
from LibreHardwareMonitor.Hardware import Computer

hw_computer = Computer()
hw_computer.IsCpuEnabled = True
hw_computer.Open()

def get_cpu_temp():
    for hardware in hw_computer.Hardware:
        hardware.Update()
        for sensor in hardware.Sensors:
            if sensor.SensorType.ToString() == "Temperature" and sensor.Name == "CPU Package":
                return sensor.Value
    return None

# ---------- Загрузка ML-модели предсказания FPS ----------
fps_bundle = joblib.load("fps_model.pkl")
fps_model = fps_bundle["model"]
fps_name_to_code = fps_bundle["name_to_code"]
fps_games = fps_bundle["games"]
settings_order = fps_bundle["settings_order"]

RESOLUTIONS = {
    "1920x1080 (1080p)": 1920 * 1080,
    "2560x1440 (1440p)": 2560 * 1440,
    "3840x2160 (4K)": 3840 * 2160,
}

# ---------- Окно ----------
window = tk.Tk()
window.title("CanIPlay")
window.geometry("820x900")

title = tk.Label(window, text="CanIPlay", font=("Arial", 24, "bold"))
title.pack(pady=15)

cpu_count = psutil.cpu_count()
ram_gb = psutil.virtual_memory().total / (1024**3)
gpus = GPUtil.getGPUs()
detected_gpu_name = gpus[0].name if gpus else "Unknown"

# ---------- Блок железа ----------
hw_frame = tk.LabelFrame(window, text="Твоё железо", font=("Arial", 12))
hw_frame.pack(padx=20, pady=8, fill="x")

cpu_label = tk.Label(hw_frame, text=f"CPU: {cpu_count} ядер", font=("Arial", 11))
cpu_label.pack(anchor="w", padx=10, pady=3)
ram_label = tk.Label(hw_frame, text=f"RAM: {ram_gb:.1f} GB", font=("Arial", 11))
ram_label.pack(anchor="w", padx=10, pady=3)
gpu_label = tk.Label(hw_frame, text=f"GPU: {detected_gpu_name}, VRAM: {gpus[0].memoryTotal} MB", font=("Arial", 11))
gpu_label.pack(anchor="w", padx=10, pady=3)

# ---------- Определяем карту для модели (гибрид) ----------
def find_gpu_in_specs(name):
    """Ищем карту в справочнике: точное совпадение, потом частичное."""
    if name in GPU_SPECS:
        return name
    # частичный поиск: убираем слова и сравниваем
    name_low = name.lower()
    for spec_name in GPU_SPECS:
        if spec_name.lower() in name_low or name_low in spec_name.lower():
            return spec_name
    return None

matched_gpu = find_gpu_in_specs(detected_gpu_name)

# ---------- Блок предсказания FPS ----------
fps_frame = tk.LabelFrame(window, text="Предсказание FPS", font=("Arial", 12))
fps_frame.pack(padx=20, pady=8, fill="x")

# выбор карты (по умолчанию определённая; если не нашли — выбор вручную)
tk.Label(fps_frame, text="Видеокарта:", font=("Arial", 10)).pack(anchor="w", padx=10)
gpu_choice_var = tk.StringVar()
gpu_names_sorted = sorted(GPU_SPECS.keys())
if matched_gpu:
    gpu_choice_var.set(matched_gpu)
    note = f"Карта определена: {matched_gpu}"
else:
    gpu_choice_var.set(gpu_names_sorted[0])
    note = f"Карта '{detected_gpu_name}' не найдена в базе — выбери похожую"
gpu_note_label = tk.Label(fps_frame, text=note, font=("Arial", 9), fg="gray")
gpu_note_label.pack(anchor="w", padx=10)
gpu_choice_menu = tk.OptionMenu(fps_frame, gpu_choice_var, *gpu_names_sorted)
gpu_choice_menu.pack(anchor="w", padx=10, pady=3, fill="x")

# выбор игры (из 104 игр модели)
tk.Label(fps_frame, text="Игра:", font=("Arial", 10)).pack(anchor="w", padx=10)
fps_game_var = tk.StringVar(value=fps_games[0])
fps_game_menu = tk.OptionMenu(fps_frame, fps_game_var, *fps_games)
fps_game_menu.pack(anchor="w", padx=10, pady=3, fill="x")

# настройки графики
tk.Label(fps_frame, text="Настройки графики:", font=("Arial", 10)).pack(anchor="w", padx=10)
settings_var = tk.StringVar(value="high")
settings_menu = tk.OptionMenu(fps_frame, settings_var, "low", "medium", "high", "ultra")
settings_menu.pack(anchor="w", padx=10, pady=3, fill="x")

# разрешение
tk.Label(fps_frame, text="Разрешение:", font=("Arial", 10)).pack(anchor="w", padx=10)
res_var = tk.StringVar(value="1920x1080 (1080p)")
res_menu = tk.OptionMenu(fps_frame, res_var, *RESOLUTIONS.keys())
res_menu.pack(anchor="w", padx=10, pady=3, fill="x")

fps_result_label = tk.Label(fps_frame, text="", font=("Arial", 16, "bold"))
fps_result_label.pack(pady=8)

fps_note_label = tk.Label(fps_frame,
    text="Оценка для нативного рендеринга (без DLSS / Frame Gen). С DLSS будет выше.",
    font=("Arial", 8), fg="gray")
fps_note_label.pack()

def predict_fps():
    spec = GPU_SPECS[gpu_choice_var.get()]
    row = pd.DataFrame([{
        "perf_1080": spec["perf_1080"],
        "perf_1440": spec["perf_1440"],
        "perf_4k": spec["perf_4k"],
        "vram": spec["vram"],
        "year": spec["year"],
        "res_pixels": RESOLUTIONS[res_var.get()],
        "settings_num": settings_order[settings_var.get()],
        "game_code": fps_name_to_code[fps_game_var.get()],
    }])[fps_bundle["features"]]
    fps = fps_model.predict(row)[0]

    # цвет по играбельности
    if fps >= 60:
        color = "green"
    elif fps >= 30:
        color = "orange"
    else:
        color = "red"
    fps_result_label.config(text=f"~ {fps:.0f} FPS", fg=color)

predict_btn = tk.Button(fps_frame, text="Предсказать FPS", font=("Arial", 12, "bold"),
                        bg="#2563eb", fg="white", command=predict_fps)
predict_btn.pack(pady=8)

# ---------- Старая проверка по требованиям (оставляем) ----------
game_frame = tk.LabelFrame(window, text="Проверка совместимости", font=("Arial", 12))
game_frame.pack(padx=20, pady=8, fill="x")

from game_data import games
game_var = tk.StringVar(value=list(games.keys())[0])
game_menu = tk.OptionMenu(game_frame, game_var, *games.keys())
game_menu.pack(padx=10, pady=5)

result_label = tk.Label(game_frame, text="", font=("Arial", 13, "bold"))
result_label.pack(pady=5)

def check_game():
    game_name = game_var.get()
    req = games[game_name]
    if cpu_count >= req['min_cpu_cores'] and ram_gb >= req['min_ram_gb'] and gpus[0].memoryTotal >= req['min_vram_mb']:
        result_label.config(text=f"✅ {game_name}: True", fg="green")
    else:
        result_label.config(text=f"❌ {game_name}: False", fg="red")

check_btn = tk.Button(game_frame, text="Проверить!", font=("Arial", 11, "bold"),
                      bg="green", fg="white", command=check_game)
check_btn.pack(pady=8)

# ---------- Температуры ----------
temp_frame = tk.LabelFrame(window, text="Температуры (реальное время)", font=("Arial", 12))
temp_frame.pack(padx=20, pady=8, fill="x")

cpu_temp_label = tk.Label(temp_frame, text="CPU: --°C", font=("Arial", 11))
cpu_temp_label.pack(anchor="w", padx=10, pady=3)
gpu_temp_label = tk.Label(temp_frame, text="GPU: --°C", font=("Arial", 11))
gpu_temp_label.pack(anchor="w", padx=10, pady=3)

def update_temps():
    g = GPUtil.getGPUs()
    if g:
        gpu_temp_label.config(text=f"GPU: {g[0].temperature}°C | Нагрузка: {g[0].load*100:.0f}%")
    cpu_temp = get_cpu_temp()
    if cpu_temp is not None:
        cpu_temp_label.config(text=f"CPU: {cpu_temp:.0f}°C | Нагрузка: {psutil.cpu_percent()}%")
    else:
        cpu_temp_label.config(text=f"CPU: --°C | Нагрузка: {psutil.cpu_percent()}%")
    window.after(1000, update_temps)

update_temps()
window.mainloop()
