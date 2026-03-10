# opcua_server.py
import sqlite3
import time
import struct
from opcua import Server
from pymodbus.client.sync import ModbusTcpClient

# --- OPC UA Server Setup ---
server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840")

uri = "http://example.org"
idx = server.register_namespace(uri)

objects = server.get_objects_node()
device = objects.add_object(idx, "VirtualSensors")

temperature = device.add_variable(idx, "Temperature", 0.0)
humidity = device.add_variable(idx, "Humidity", 0.0)
pressure = device.add_variable(idx, "Pressure", 0.0)

temperature.set_writable()
humidity.set_writable()
pressure.set_writable()

# --- Modbus Client Setup ---
client = ModbusTcpClient("127.0.0.1", port=5020)
if not client.connect():
    print("Ошибка подключения к Modbus")
    exit(1)

# --- SQLite Setup ---
conn = sqlite3.connect("sensors.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# --- Start OPC UA Server ---
server.start()
print("OPC UA server started at port 4840")

try:
    while True:
        # Чтение 4 регистров: t(0), h(1), p(2+3)
        result = client.read_holding_registers(0, 4)
        if result.isError():
            print("Ошибка чтения Modbus:", result)
            time.sleep(2)
            continue

        if len(result.registers) < 4:
            print("Недостаточно регистров Modbus")
            time.sleep(2)
            continue

        # Температура и влажность 16-bit
        t = result.registers[0]
        h = result.registers[1]

        # Давление собираем из двух 16-bit регистров
        pressure_int = (result.registers[2] << 16) + result.registers[3]
        p = pressure_int / 100.0   # масштаб 100

        # Обновление OPC UA
        temperature.set_value(t)
        humidity.set_value(h)
        pressure.set_value(p)
        print(f"OPCUA Updated: Temperature={t}, Humidity={h}, Pressure={p:.2f}")

        # Запись в SQLite
        cursor.execute(
            "INSERT INTO sensors(temperature,humidity,pressure) VALUES(?,?,?)",
            (t, h, p)
        )
        conn.commit()

        time.sleep(2)

finally:
    print("Остановка сервера...")
    server.stop()
    client.close()
    conn.close()
