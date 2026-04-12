import logging
import time
from pymodbus.client.sync import ModbusTcpClient

logger = logging.getLogger(__name__)


class ModbusClient:
    """
    Клиент для чтения регистров Modbus TCP.
    Поддерживает автоматическое переподключение при сбоях.
    """

    def __init__(self, host: str, port: int, slave_id: int,
                 timeout: int = 3, retry_count: int = 3):
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self.retry_count = retry_count
        self.client = ModbusTcpClient(self.host, port=self.port)

    def connect(self) -> bool:
        """Подключиться к Modbus-серверу. Возвращает True при успехе."""
        for attempt in range(1, self.retry_count + 1):
            if self.client.connect():
                logger.info(f"Modbus: подключение к {self.host}:{self.port} установлено")
                return True
            logger.warning(f"Modbus: попытка {attempt}/{self.retry_count} неудачна")
            time.sleep(1)

        logger.error(f"Modbus: не удалось подключиться к {self.host}:{self.port}")
        return False

    def read_register(self, address: int) -> int | None:
        """
        Читает один holding-регистр по адресу.
        При ошибке пытается переподключиться и возвращает None.
        """
        result = self.client.read_holding_registers(
            address, count=1, unit=self.slave_id
        )

        if result is None or result.isError():
            logger.warning(f"Modbus: ошибка чтения регистра {address}, пробую переподключиться...")
            self.connect()
            return None

        value = result.registers[0]
        logger.debug(f"Modbus: регистр {address} = {value}")
        return value

    def read_registers(self, addresses: list[int]) -> dict[int, int | None]:
        """Читает несколько регистров за один вызов."""
        return {addr: self.read_register(addr) for addr in addresses}

    def close(self):
        """Закрыть соединение."""
        self.client.close()
        logger.info("Modbus: соединение закрыто")
