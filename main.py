import psutil
import GPUtil
print(psutil.cpu_count())
print(psutil.virtual_memory().total)
ram_gb = psutil.virtual_memory().total / (1024**3)
print(f"RAM: {ram_gb:.1f} GB")
cpu_count = psutil.cpu_count()
print(f"CPU ядер: {cpu_count}")
gpus = GPUtil.getGPUs()
for gpu in gpus:
    print(f"GPU: {gpu.name}, VRAM: {gpu.memoryTotal} MB")
from game_data import games 
def check_game(game_name):
    req = games[game_name]
    if cpu_count >= req['min_cpu_cores'] and ram_gb >= req['min_ram_gb']:
        print(f"{game_name}: Потянет!")
    else:
        print(f"{game_name}: Не потянет!")

check_game("Arma Reforger")

