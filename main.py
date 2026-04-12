import asyncio
import logging
import uvicorn
from modbus_client import ModbusClient
from opcua_server import OPCUAServer
from database import Database
from api_server import app

# --- ГЛОБАЛЬНЫЕ НАСТРОЙКИ ---
CONFIG = {
    "modbus": {"host": "172.20.10.4", "port": 5020, "slave_id": 1},
    "opcua": {"endpoint": "opc.tcp://0.0.0.0:4840", "namespace": "IndustrialGateway", "device_name": "VirtualSensor"},
    "api": {"host": "127.0.0.1", "port": 8000},
    "database": {"path": "sensors.db"}
}

# Маппинг с проверкой границ (min/max)
MAPPING = {
    "temperature": {"register": 0, "unit": "C", "min": -20, "max": 80},
    "humidity": {"register": 1, "unit": "%", "min": 0, "max": 100},
    "pressure": {"register": 2, "unit": "hPa", "min": 900, "max": 1100},
    "level": {"register": 3, "unit": "m", "min": 0, "max": 10}
}

# Событие для плавной остановки через GUI
stop_event = asyncio.Event()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("main")

async def polling_loop(modbus, opcua, db, mapping):
    """Цикл опроса датчиков"""
    logger.info("Цикл опроса запущен")
    while not stop_event.is_set():
        try:
            for name, meta in mapping.items():
                value = modbus.read_register(meta["register"])
                if value is not None:
                    # Проверка границ
                    if "min" in meta and value < meta["min"]:
                        raise ValueError(f"НИЗКИЙ ПОКАЗАТЕЛЬ {name}: {value}{meta['unit']}")
                    if "max" in meta and value > meta["max"]:
                        raise ValueError(f"ВЫСОКИЙ ПОКАЗАТЕЛЬ {name}: {value}{meta['unit']}")

                    await opcua.update(name, value)
                    db.save(name, value)
                    logger.info(f"Считано: {name} = {value} {meta['unit']}")
            
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Ошибка в цикле опроса: {e}")
            await asyncio.sleep(5)

async def main():
    """Основная функция запуска"""
    # 1. Инициализация
    modbus = ModbusClient(host=CONFIG["modbus"]["host"], port=CONFIG["modbus"]["port"], slave_id=CONFIG["modbus"]["slave_id"])
    if not modbus.connect():
        logger.error("Не удалось подключиться к Modbus-симулятору!")
        return

    opcua = OPCUAServer()
    await opcua.start()
    db = Database(CONFIG["database"]["path"])

    # 2. Настройка API
    api_config = uvicorn.Config(app, host=CONFIG["api"]["host"], port=CONFIG["api"]["port"], log_level="error")
    api_server = uvicorn.Server(api_config)

    logger.info("="*40)
    logger.info("ШЛЮЗ ЗАПУЩЕН И ГОТОВ К РАБОТЕ")
    logger.info("="*40)

    try:
        # Запускаем задачи и ждем установки флага stop_event
        # Мы используем create_task для API, чтобы оно работало в фоне
        api_task = asyncio.create_task(api_server.serve())
        poll_task = asyncio.create_task(polling_loop(modbus, opcua, db, MAPPING))

        # Ждем, пока GUI не скажет "стоп"
        while not stop_event.is_set():
            await asyncio.sleep(0.5)
            if api_task.done() or poll_task.done(): # Если что-то упало само
                break

        # Отменяем задачи при остановке
        poll_task.cancel()
        api_server.should_exit = True
        await api_task

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        logger.info("Закрытие соединений...")
        modbus.close()
        # Тут можно добавить opcua.stop() если в классе есть такой метод

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Принудительное завершение пользователем")
