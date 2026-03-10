# modbus_server.py
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
import random
import time
from threading import Thread

def update_registers(context):
    while True:
        # Генерация случайных данных для примера
        temperature = random.randint(20, 30)      # 20–30 °C
        humidity = random.randint(40, 60)         # 40–60 %
        pressure = random.randint(1000, 1020)     # давление hPa

        # Давление 32-bit хранится в двух регистрах
        pressure_int = int(pressure * 100)        # масштаб 100
        pressure_high = (pressure_int >> 16) & 0xFFFF
        pressure_low = pressure_int & 0xFFFF

        # Запись регистров: адреса 0,1,2,3
        context[0x00].setValues(3, 0, [temperature, humidity, pressure_high, pressure_low])

        time.sleep(2)

# Создаем блок данных Modbus
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*10),  # 10 holding регистров
    zero_mode=True
)
context = ModbusServerContext(slaves=store, single=True)

# Запуск потока обновления регистров
thread = Thread(target=update_registers, args=(context,))
thread.daemon = True
thread.start()

# Запуск Modbus TCP сервера
print("Modbus TCP сервер запущен на порту 5020")
StartTcpServer(context, address=("0.0.0.0", 5020))
