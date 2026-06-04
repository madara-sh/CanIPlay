import os
import tkinter as tk
from tkinter import ttk
import psutil
import GPUtil
import clr
import joblib
import pandas as pd

from gpu_specs import GPU_SPECS
from rtx50_patch import RTX_50_SERIES
GPU_SPECS.update(RTX_50_SERIES)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

fps_bundle = joblib.load(os.path.join(BASE_DIR, "fps_model.pkl"))
fps_model = fps_bundle["model"]
fps_name_to_code = fps_bundle["name_to_code"]
fps_games = fps_bundle["games"]
settings_order = fps_bundle["settings_order"]

RESOLUTIONS = {
    "1920x1080 (1080p)": 1920 * 1080,
    "2560x1440 (1440p)": 2560 * 1440,
    "3840x2160 (4K)": 3840 * 2160,
}

def make_searchable_combo(parent, values, initial):
    var = tk.StringVar(value=initial)
    combo = ttk.Combobox(parent, textvariable=var, values=values, state="normal")

    def on_keyrelease(event):
        if event.keysym in ("Up", "Down", "Return", "Escape", "Left", "Right"):
            return
        typed = var.get().lower()
        if typed == "":
            combo["values"] = values
        else:
            filtered = [v for v in values if typed in v.lower()]
            combo["values"] = filtered if filtered else values

    combo.bind("<KeyRelease>", on_keyrelease)
    return combo, var

window = tk.Tk()
window.title("CanIPlay")
window.geometry("560x620")

title = tk.Label(window, text="CanIPlay", font=("Arial", 20, "bold"))
title.pack(pady=8)

cpu_count = psutil.cpu_count()
ram_gb = psutil.virtual_memory().total / (1024**3)
gpus = GPUtil.getGPUs()
detected_gpu_name = gpus[0].name if gpus else "Unknown"

hw_frame = tk.LabelFrame(window, text="Your Hardware", font=("Arial", 11))
hw_frame.pack(padx=12, pady=5, fill="x")

tk.Label(hw_frame, text=f"CPU: {cpu_count} cores", font=("Arial", 10)).pack(anchor="w", padx=8, pady=1)
tk.Label(hw_frame, text=f"RAM: {ram_gb:.1f} GB", font=("Arial", 10)).pack(anchor="w", padx=8, pady=1)
tk.Label(hw_frame, text=f"GPU: {detected_gpu_name}, VRAM: {gpus[0].memoryTotal} MB", font=("Arial", 10)).pack(anchor="w", padx=8, pady=1)

def find_gpu_in_specs(name):
    if name in GPU_SPECS:
        return name
    name_low = name.lower()
    for spec_name in GPU_SPECS:
        if spec_name.lower() in name_low or name_low in spec_name.lower():
            return spec_name
    return None

matched_gpu = find_gpu_in_specs(detected_gpu_name)

fps_frame = tk.LabelFrame(window, text="FPS Prediction", font=("Arial", 11))
fps_frame.pack(padx=12, pady=5, fill="x")

tk.Label(fps_frame, text="Graphics Card:", font=("Arial", 9)).pack(anchor="w", padx=8)
gpu_names_sorted = sorted(GPU_SPECS.keys())
gpu_initial = matched_gpu if matched_gpu else gpu_names_sorted[0]
if matched_gpu:
    note = f"Detected: {matched_gpu}"
else:
    note = f"'{detected_gpu_name}' not found - type to search"
tk.Label(fps_frame, text=note, font=("Arial", 8), fg="gray").pack(anchor="w", padx=8)
gpu_combo, gpu_choice_var = make_searchable_combo(fps_frame, gpu_names_sorted, gpu_initial)
gpu_combo.pack(anchor="w", padx=8, pady=2, fill="x")

tk.Label(fps_frame, text="Game (type to search):", font=("Arial", 9)).pack(anchor="w", padx=8)
game_combo, fps_game_var = make_searchable_combo(fps_frame, fps_games, fps_games[0])
game_combo.pack(anchor="w", padx=8, pady=2, fill="x")

settings_res_row = tk.Frame(fps_frame)
settings_res_row.pack(fill="x", padx=8, pady=2)

settings_col = tk.Frame(settings_res_row)
settings_col.pack(side="left", expand=True, fill="x", padx=(0, 4))
tk.Label(settings_col, text="Settings:", font=("Arial", 9)).pack(anchor="w")
settings_var = tk.StringVar(value="high")
ttk.Combobox(settings_col, textvariable=settings_var,
             values=["low", "medium", "high", "ultra"], state="readonly").pack(fill="x")

res_col = tk.Frame(settings_res_row)
res_col.pack(side="left", expand=True, fill="x", padx=(4, 0))
tk.Label(res_col, text="Resolution:", font=("Arial", 9)).pack(anchor="w")
res_var = tk.StringVar(value="1920x1080 (1080p)")
ttk.Combobox(res_col, textvariable=res_var,
             values=list(RESOLUTIONS.keys()), state="readonly").pack(fill="x")

def predict_fps():
    gpu_name = gpu_choice_var.get()
    game_name = fps_game_var.get()
    if gpu_name not in GPU_SPECS:
        fps_result_label.config(text="Pick a valid card", fg="red")
        return
    if game_name not in fps_name_to_code:
        fps_result_label.config(text="Pick a valid game", fg="red")
        return
    spec = GPU_SPECS[gpu_name]
    row = pd.DataFrame([{
        "perf_1080": spec["perf_1080"],
        "perf_1440": spec["perf_1440"],
        "perf_4k": spec["perf_4k"],
        "vram": spec["vram"],
        "year": spec["year"],
        "res_pixels": RESOLUTIONS[res_var.get()],
        "settings_num": settings_order[settings_var.get()],
        "game_code": fps_name_to_code[game_name],
    }])[fps_bundle["features"]]
    fps = fps_model.predict(row)[0]

    if fps >= 60:
        color = "green"
    elif fps >= 30:
        color = "orange"
    else:
        color = "red"
    fps_result_label.config(text=f"~ {fps:.0f} FPS", fg=color)

tk.Button(fps_frame, text="Predict FPS", font=("Arial", 11, "bold"),
          bg="#2563eb", fg="white", command=predict_fps).pack(pady=6)

fps_result_label = tk.Label(fps_frame, text="", font=("Arial", 16, "bold"))
fps_result_label.pack()

tk.Label(fps_frame,
         text="Native rendering estimate (no DLSS / Frame Gen). With DLSS it will be higher.",
         font=("Arial", 8), fg="gray").pack(pady=(0, 4))

temp_frame = tk.LabelFrame(window, text="Temperatures (live)", font=("Arial", 11))
temp_frame.pack(padx=12, pady=5, fill="x")

cpu_temp_label = tk.Label(temp_frame, text="CPU: --C", font=("Arial", 10))
cpu_temp_label.pack(anchor="w", padx=8, pady=1)
gpu_temp_label = tk.Label(temp_frame, text="GPU: --C", font=("Arial", 10))
gpu_temp_label.pack(anchor="w", padx=8, pady=1)

def update_temps():
    g = GPUtil.getGPUs()
    if g:
        gpu_temp_label.config(text=f"GPU: {g[0].temperature}C | Load: {g[0].load*100:.0f}%")
    cpu_temp = get_cpu_temp()
    if cpu_temp is not None:
        cpu_temp_label.config(text=f"CPU: {cpu_temp:.0f}C | Load: {psutil.cpu_percent()}%")
    else:
        cpu_temp_label.config(text=f"CPU: --C | Load: {psutil.cpu_percent()}%")
    window.after(1000, update_temps)

update_temps()
window.mainloop()
