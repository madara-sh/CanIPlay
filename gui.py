import tkinter as tk
import psutil
import GPUtil
import clr

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

window = tk.Tk()
window.title("CanIPlay")
window.geometry("800x600")

title = tk.Label(window, text="CanIPlay", font=("Arial", 24, "bold"))
title.pack(pady=20)

cpu_count = psutil.cpu_count()
ram_gb = psutil.virtual_memory().total / (1024**3)
gpus = GPUtil.getGPUs()

hw_frame = tk.LabelFrame(window, text="CPU", font=("Arial", 12))
hw_frame.pack(padx=20, pady=10, fill="x")

cpu_label = tk.Label(hw_frame, text=f"CPU: {psutil.cpu_count()} ядер", font=("Arial", 11))
cpu_label.pack(anchor="w", padx=10, pady=5)

ram_gb = psutil.virtual_memory().total / (1024**3)
ram_label = tk.Label(hw_frame, text=f"RAM: {ram_gb:.1f} GB", font=("Arial", 11))
ram_label.pack(anchor="w", padx=10, pady=5)

gpus = GPUtil.getGPUs()
gpu_text = f"GPU: {gpus[0].name}, VRAM: {gpus[0].memoryTotal} MB"
gpu_label = tk.Label(hw_frame, text=gpu_text, font=("Arial", 11))
gpu_label.pack(anchor="w", padx=10, pady=5)

game_frame = tk.LabelFrame(window, text="Game", font=("Arial", 12))
game_frame.pack(padx=20, pady=10, fill="x")

from game_data import games
game_var = tk.StringVar(value=list(games.keys())[0])
game_menu = tk.OptionMenu(game_frame, game_var, *games.keys())
game_menu.pack(padx=10, pady=5)

result_label = tk.Label(window, text="", font=("Arial", 14, "bold"))
result_label.pack(pady=10)

def check_game():
    game_name = game_var.get()
    req = games[game_name]
    if cpu_count >= req['min_cpu_cores'] and ram_gb >= req['min_ram_gb'] and gpus[0].memoryTotal >= req['min_vram_mb']:
        result_label.config(text=f"✅ {game_name}: True", fg="green")
    else:
        result_label.config(text=f"❌ {game_name}: False", fg="red")

check_btn = tk.Button(window, text="Проверить!", font=("Arial", 12, "bold"), bg="green", fg="white", command=check_game)
check_btn.pack(pady=20)



temp_frame = tk.LabelFrame(window, text="Температуры", font=("Arial", 12))
temp_frame.pack(padx=20, pady=10, fill="x")

cpu_temp_label = tk.Label(temp_frame, text="CPU: --°C", font=("Arial", 11))
cpu_temp_label.pack(anchor="w", padx=10, pady=5)

gpu_temp_label = tk.Label(temp_frame, text="GPU: --°C", font=("Arial", 11))
gpu_temp_label.pack(anchor="w", padx=10, pady=5)

def update_temps():
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu_temp_label.config(text=f"GPU: {gpus[0].temperature}°C | Нагрузка: {gpus[0].load*100:.0f}%")

    cpu_temp = get_cpu_temp()
    if cpu_temp is not None:
        cpu_temp_label.config(text=f"CPU: {cpu_temp:.0f}°C | Нагрузка: {psutil.cpu_percent()}%")
    else:
        cpu_temp_label.config(text=f"CPU: --°C | Нагрузка: {psutil.cpu_percent()}%")

    window.after(1000, update_temps)

update_temps()  


window.mainloop()