from asyncua import Server


class OPCUAServer:

    def __init__(self):

        self.server = Server()
        self.variables = {}

    async def start(self):

        await self.server.init()

        self.server.set_endpoint("opc.tcp://0.0.0.0:4840")

        uri = "IndustrialGateway"

        idx = await self.server.register_namespace(uri)

        objects = self.server.nodes.objects

        device = await objects.add_object(idx, "ModbusDevice")

        self.variables["temperature"] = await device.add_variable(idx, "Temperature", 0)
        self.variables["pressure"] = await device.add_variable(idx, "Pressure", 0)

        for v in self.variables.values():
            await v.set_writable()

        await self.server.start()

    async def update(self, name, value):

        if name in self.variables:
            await self.variables[name].write_value(value)
