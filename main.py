import asyncio
import yaml

from modbus.modbus_client import ModbusClient
from opcua.opcua_server import OPCUAServer
from core.data_mapper import DataMapper


async def main():

    mapper = DataMapper("config/config.yaml")
    mapping = mapper.mapping()

    with open("config/config.yaml") as f:
        config = yaml.safe_load(f)

    modbus = ModbusClient(
        config["modbus"]["host"],
        config["modbus"]["port"],
        config["modbus"]["slave_id"]
    )

    modbus.connect()

    opcua = OPCUAServer()
    await opcua.start()

    while True:

        for name, item in mapping.items():

            value = modbus.read_register(item["register"])

            if value is not None:

                await opcua.update(name, value)

        await asyncio.sleep(1)


asyncio.run(main())
