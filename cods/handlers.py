"""
Этот модуль реализует бота-напоминателя с использованием библиотеки aiogram.

Функции бота:
- Обработка команд /start и /help для взаимодействия бота с пользователем.
- Добавление новых напоминаний с указанием времени и текста.
- Просмотр всех установленных пользователем напоминаний.
- Отправка напоминаний в указанное время.

Структура данных для хранения напоминаний:
- reminders: словарь, где ключом является ID пользователя, а значением - список напоминаний.
"""
import asyncio
#импорт всего необходимого из библиотеки аиограм
from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
import datetime
import keyboards

#структура данных для хранения напоминаний
reminders = {}
router = Router()  #маршрутизатор


@router.message(Command('start'))
async def cmd_start(message: Message):
    """Обрабатывает команду /start и отправляет приветственное сообщение."""
    await message.answer('Привет! Я - Бот-напоминатель. Отправь мне команду /help, чтобы начать использование.')


@router.message(Command('help'))
async def cmd_help(message: Message):
    """Обрабатывает команду /help и отправляет информацию о возможностях бота."""
    help_text = (
        "✋ Что я умею:\n\n"
        "1. Добавить напоминание - Нажав на эту кнопку, ты сможешь установить новое напоминание с указанием времени и текста.\n"
        "2. Просмотреть все напоминания - После нажатия этой кнопки тебе высветится список всех установленных тобой напоминаний.\n\n"
        "📝 Я постараюсь напомнить тебе о важных событиях!"
    )

    await message.answer(help_text, reply_markup=keyboards.main)

@router.message(F.text == 'Добавить напоминание')
async def add_reminder(message: Message):
    """Добавляет новое напоминание для пользователя."""
    if message.from_user.id not in reminders:
        reminders[message.from_user.id] = []

    reminders[message.from_user.id].append({'waiting_for_datetime': True})
    await message.answer("Когда ты хочешь, чтобы я напомнил тебе? (напиши дату и время в формате 'YYYY-MM-DD HH:MM')")


@router.message(F.text == 'Просмотреть все напоминания')
async def view_reminders(message: Message):
    """Позволяет пользователю просмотреть все установленные напоминания."""
    user_id = message.from_user.id
    user_reminders = reminders.get(user_id, [])

    if not user_reminders:
        await message.answer("У вас нет установленных напоминаний.")
        return

    reminders_list = []
    for index, reminder in enumerate(user_reminders):
        if 'reminder_datetime' in reminder:
            reminders_list.append(
                f"{index + 1}. {reminder['reminder_datetime'].strftime('%Y-%m-%d %H:%M')}: {reminder.get('reminder_message', 'Не задано')}")

    await message.answer("\n".join(reminders_list))


@router.message()
async def process_input(message: Message):
    """Обрабатывает ввод пользователя и управляет состоянием напоминаний."""
    user_id = message.from_user.id
    if user_id not in reminders:
        reminders[user_id] = []

    #проверка на ожидание ввода даты для нового напоминания
    if reminders[user_id] and reminders[user_id][-1].get('waiting_for_datetime'):
        user_datetime = message.text
        try:
            reminder_datetime = datetime.datetime.strptime(user_datetime, '%Y-%m-%d %H:%M')
            reminders[user_id][-1]['reminder_datetime'] = reminder_datetime
            reminders[user_id][-1]['waiting_for_datetime'] = False
            await message.answer("Что ты хочешь, чтобы я напомнил тебе?")
        except ValueError:
            await message.reply("Неправильный формат даты и времени. Пожалуйста, используй формат 'YYYY-MM-DD HH:MM'.")
            return

    #проверка наличия установленного времени для напоминания
    elif reminders[user_id] and 'reminder_datetime' in reminders[user_id][-1]:
        reminder_message = message.text
        reminders[user_id][-1]['reminder_message'] = reminder_message  #сохраняем текст сообщения напоминания

        reminder_datetime = reminders[user_id][-1]['reminder_datetime']
        now = datetime.datetime.now()
        if reminder_datetime < now:
            reminder_datetime += datetime.timedelta(days=1)

        await message.reply(f"Напоминание установлено на {reminder_datetime.strftime('%Y-%m-%d %H:%M')}.")

        #задача для отправки напоминания
        await asyncio.create_task(send_reminder(message.bot, user_id, reminder_datetime, reminder_message))

    else:
        await message.answer("Я не понимаю, что ты имеешь в виду.")


async def send_reminder(bot: Bot, user_id: int, reminder_datetime: datetime.datetime, reminder_message: str):
    """Отправляет напоминание пользователю в нужное время."""
    await asyncio.sleep((reminder_datetime - datetime.datetime.now()).total_seconds())

    if user_id in reminders and reminders[user_id]:
        await bot.send_message(user_id, f"Напоминание: {reminder_message}")

