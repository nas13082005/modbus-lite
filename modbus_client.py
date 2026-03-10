from pymodbus.client.sync import ModbusTcpClient

client = ModbusTcpClient("127.0.0.1",port=5020)

client.connect()

result = client.read_holding_registers(0,3)

print("Temperature:",result.registers[0])
print("Humidity:",result.registers[1])
print("Pressure:",result.registers[2])

client.close()
