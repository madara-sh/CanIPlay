import clr  # это из pythonnet


dll_path = r"C:\Users\mlbeast\Downloads\LibreHardwareMonitor\LibreHardwareMonitorLib.dll"
clr.AddReference(dll_path)

from LibreHardwareMonitor.Hardware import Computer

computer = Computer()
computer.IsCpuEnabled = True
computer.Open()

cpu_temp = None
for hardware in computer.Hardware:
    hardware.Update()
    for sensor in hardware.Sensors:
        
       if sensor.SensorType.ToString() == "Temperature" and sensor.Name == "CPU Package":
            cpu_temp = sensor.Value

if cpu_temp is not None:
    print(f"Температура CPU: {cpu_temp:.1f}°C")
else:
    print("Не нашёл CPU Core — выведу все датчики температуры:")
    for hardware in computer.Hardware:
        for sensor in hardware.Sensors:
            if sensor.SensorType.ToString() == "Temperature":
                print(f"  {sensor.Name}: {sensor.Value}")

computer.Close()