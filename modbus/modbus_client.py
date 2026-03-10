from pymodbus.client.sync import ModbusTcpClient


class ModbusClient:

    def __init__(self, host, port, slave_id):

        self.client = ModbusTcpClient(host, port=port)
        self.slave_id = slave_id

    def connect(self):

        return self.client.connect()

    def read_register(self, address):

        result = self.client.read_holding_registers(
            address,
            1,
            unit=self.slave_id
        )

        if result.isError():
            return None

        return result.registers[0]
