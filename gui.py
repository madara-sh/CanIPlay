import tkinter as tk
import psutil
import GPUtil

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

game_frame = tk.LabelFrame(window, text="Выбери игру", font=("Arial", 12))
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
        result_label.config(text=f"✅ {game_name}: Потянет!", fg="green")
    else:
        result_label.config(text=f"❌ {game_name}: Не потянет!", fg="red")

check_btn = tk.Button(window, text="Проверить!", font=("Arial", 12, "bold"), bg="green", fg="white", command=check_game)
check_btn.pack(pady=20)

window.mainloop()