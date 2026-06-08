import customtkinter as ctk
import psutil
import GPUtil
import joblib
import pandas as pd
import os
from tkinter import ttk
import tkinter as tk
from gpu_specs import GPU_SPECS
from rtx50_patch import RTX_50_SERIES
GPU_SPECS.update(RTX_50_SERIES)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

def find_gpu_in_specs(name):
    if name in GPU_SPECS:
        return name
    name_low = name.lower()
    for spec_name in GPU_SPECS:
        if spec_name.lower() in name_low or name_low in spec_name.lower():
            return spec_name
    return None

ctk.set_appearance_mode("dark")
window = ctk.CTk()
window.title('CanIPlay')
window.geometry("560x620")
title = ctk.CTkLabel(window, text="CanIPlay", font=ctk.CTkFont(size=24, weight="bold"))
title.pack(pady=10)
cpu_count = psutil.cpu_count()
ram_gb = psutil.virtual_memory().total / (1024**3)
gpus = GPUtil.getGPUs()
detected_gpu_name = gpus[0].name if gpus else "Unknown"
hw_frame = ctk.CTkFrame(window)
hw_frame.pack(pady=5, padx=12, fill="x")
hw_title = ctk.CTkLabel(hw_frame, text=f"Your Hardware", font=ctk.CTkFont(size=16, weight="bold"))
hw_title.pack(anchor="w", padx=8, pady=(5, 2))
cpu_label = ctk.CTkLabel(hw_frame, text=f"CPU: {cpu_count} cores")
cpu_label.pack(anchor="w", padx=8, pady=2)
ram_label = ctk.CTkLabel(hw_frame, text=f"RAM: {ram_gb:.1f} GB")
ram_label.pack(anchor="w", padx=8, pady=2)
gpu_label = ctk.CTkLabel(hw_frame, text=f"GPU: {gpus[0].name}, VRAM: {gpus[0].memoryTotal} MB")
gpu_label.pack(anchor="w", padx=8, pady=2)
matched_gpu = find_gpu_in_specs(detected_gpu_name)
fps_frame = ctk.CTkFrame(window)
fps_frame.pack(pady=5, padx=12, fill="x")
fps_title = ctk.CTkLabel(fps_frame, text=f"FPS Prediction", font=ctk.CTkFont(size=14, weight="bold"))
fps_title.pack(anchor="w", padx=6, pady=(4, 1))
gpu_names_sorted = sorted(GPU_SPECS.keys())
gpu_initial = matched_gpu if matched_gpu else gpu_names_sorted[0]
gpu_card_label = ctk.CTkLabel(fps_frame, text="Graphics Card:")
gpu_card_label.pack(anchor="w", padx=8)
gpu_combo, gpu_choice_var = make_searchable_combo(fps_frame, gpu_names_sorted, gpu_initial)
gpu_combo.pack(anchor="w", padx=8, pady=2, fill="x")
window.mainloop()