#импорт asyncio библиотеки, которая используется для написания асинхронного кода
import asyncio
#импорт всего необходимого из библиотеки аиограм
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router

async def main():
    #создаем бота с токеном, который я получила от BotFather
    bot = Bot(token='API_TOKEN')

    #диспетчер, который будет управлять обработкой сообщений и используем MemoryStorage для временного хранения состояний
    dp = Dispatcher(storage=MemoryStorage())

    #маршрутизатор, который содержит обработчики для различных команд и сообщений
    dp.include_router(router)

    #опрос серверов телеграмма для получения обновлений
    await dp.start_polling(bot)

if __name__ == '__main__':
    #запуск основной функции
    asyncio.run(main())
