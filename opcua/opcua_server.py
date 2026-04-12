import logging
from asyncua import Server

logger = logging.getLogger(__name__)


class OPCUAServer:
    """
    OPC UA сервер.
    Переменные создаются динамически из конфига — не захардкожены.
    """

    def __init__(self, endpoint: str, namespace: str, device_name: str):
        self.endpoint = endpoint
        self.namespace = namespace
        self.device_name = device_name
        self.server = Server()
        self.variables: dict = {}

    async def start(self, mapping: dict):
        """
        Инициализировать и запустить сервер.
        mapping — словарь вида {name: {register, unit, description, ...}}
        """
        await self.server.init()
        self.server.set_endpoint(self.endpoint)

        idx = await self.server.register_namespace(self.namespace)
        objects = self.server.nodes.objects
        device = await objects.add_object(idx, self.device_name)

        # Создаём переменные динамически из конфига
        for name, meta in mapping.items():
            var = await device.add_variable(idx, name.capitalize(), 0.0)
            await var.set_writable()
            self.variables[name] = var
            logger.info(f"OPC UA: добавлена переменная '{name}' ({meta.get('unit', '')})")

        await self.server.start()
        logger.info(f"OPC UA сервер запущен: {self.endpoint}")

    async def update(self, name: str, value: float):
        """Обновить значение переменной по имени."""
        if name not in self.variables:
            logger.warning(f"OPC UA: переменная '{name}' не зарегистрирована")
            return
        await self.variables[name].write_value(float(value))
        logger.debug(f"OPC UA: {name} = {value}")

    async def stop(self):
        """Остановить сервер."""
        await self.server.stop()
        logger.info("OPC UA сервер остановлен")
