from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.filters import Command
from aiogram import F
import logging
import random
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InputMediaPhoto
from aiogram_calendar import SimpleCalendar
from aiogram_dialog.widgets.kbd import Calendar
import aiofiles
from datetime import datetime, timedelta, date, time
import calendar
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import importlib
from config import TOKEN


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Initialize scheduler
# scheduler = AsyncIOScheduler()
# scheduler.start()

# Словари байков для каждой модели
# honda_pcx_bikes = [
#     {"name": "Honda PCX 1", "description": "Описание Honda PCX 1", "photo": "Honda PCX 1.jpg", "booked_dates": {}},
#     {"name": "Honda PCX 2", "description": "Описание Honda PCX 2", "photo": "Honda PCX 2.jpg", "booked_dates": {}},
#     {"name": "Honda PCX 3", "description": "Описание Honda PCX 3", "photo": "Honda PCX 3.jpg", "booked_dates": {}},
#     {"name": "Honda PCX 4", "description": "Описание Honda PCX 4", "photo": "Honda PCX 4.jpg", "booked_dates": {}},
#     {"name": "Honda PCX 5", "description": "Описание Honda PCX 5", "photo": "Honda PCX 5.jpg", "booked_dates": {}},
#     {"name": "Honda PCX 6", "description": "Описание Honda PCX 6", "photo": "Honda PCX 6.jpg", "booked_dates": {}},
#     {"name": "Honda PCX 7", "description": "Описание Honda PCX 7", "photo": "Honda PCX 7.jpg", "booked_dates": {}},
#     {"name": "Honda PCX 8", "description": "Описание Honda PCX 8", "photo": "Honda PCX 8.jpg", "booked_dates": {}}
# ]
#
# honda_click_bikes = [
#     {"name": "Honda Click 1", "description": "Описание Honda Click 1", "photo": "Honda Click 1.jpg",
#      "booked_dates": {}},
#     {"name": "Honda Click 2", "description": "Описание Honda Click 2", "photo": "Honda Click 2.jpg",
#      "booked_dates": {}},
#     {"name": "Honda Click 3", "description": "Описание Honda Click 3", "photo": "Honda Click 3.jpg",
#      "booked_dates": {}},
#     {"name": "Honda Click 4", "description": "Описание Honda Click 4", "photo": "Honda Click 4.jpg",
#      "booked_dates": {}},
#     # {"name": "Honda Click 5", "description": "Описание Honda Click 5", "photo": "click2.jpeg", "booked_dates": {}},
#     # {"name": "Honda Click 6", "description": "Описание Honda Click 6", "photo": "click2.jpeg", "booked_dates": {}},
#     # {"name": "Honda Click 7", "description": "Описание Honda Click 7", "photo": "click2.jpeg", "booked_dates": {}},
# ]
#
# honda_adv_bikes = [
#     {"name": "Honda ADV 1", "description": "Описание Honda ADV 1", "photo": "Honda ADV 1.jpg", "booked_dates": {}}
# ]
#
# honda_forza_bikes = [
#     {"name": "Honda Forza 1", "description": "Описание Honda Forza 1", "photo": "Honda Forza 1.jpg",
#      "booked_dates": {}},
#     {"name": "Honda Forza 2", "description": "Описание Honda Forza 2", "photo": "Honda Forza 2.jpg",
#      "booked_dates": {}},
# ]
#
# yamaha_xmax_bikes = [
#     {"name": "Yamaha Xmax 1", "description": "Описание Yamaha Xmax 1", "photo": "Yamaha Xmax 1.jpg", "booked_dates": {}}
# ]
#
# honda_scoopy_bikes = [
#     {"name": "Honda Scoopy 1", "description": "Описание Honda Scoopy 1", "photo": "Scoopy 1.jpg", "booked_dates": {}},
#     {"name": "Honda Scoopy 2", "description": "Описание Honda Scoopy 2", "photo": "Scoopy 2.jpg", "booked_dates": {}},
#     {"name": "Honda Scoopy 3", "description": "Описание Honda Scoopy 3", "photo": "Scoopy 3.jpg", "booked_dates": {}},
#     {"name": "Honda Scoopy 4", "description": "Описание Honda Scoopy 4", "photo": "Scoopy 4.jpg", "booked_dates": {}},
# ]
#
# honda_zoomer_bikes = [
#     {"name": "Honda Zoomer 1", "description": "Описание Honda Zoomer 1", "photo": "Zoomer 1.jpg", "booked_dates": {}},
#     {"name": "Honda Zoomer 2", "description": "Описание Honda Zoomer 2", "photo": "Zoomer 2.jpg", "booked_dates": {}},
# ]
#
# yamaha_fino_bikes = [
#     {"name": "Yamaha Fino", "description": "Описание Yamaha Fino", "photo": "Yamaha Fino.jpg", "booked_dates": {}},
#     {"name": "Yamaha Grand Filano", "description": "Описание Yamaha Grand Filano", "photo": "Yamaha Grand Filano.jpg",
#      "booked_dates": {}},
# ]

user_data = {}
# {519275422: {'start_date': datetime.date(2024, 8, 15), 'end_date': datetime.date(2024, 8, 18), 'bike_name': 'Honda PCX 1'}}

ADMIN_GROUP_ID = -4582383727

REVIEWS_GROUP_ID = -4268299607

REVIEWS_GROUP_LINK = '+fnrHSRyfk-A5ZmQy'


# Функция для загрузки черного списка
def load_blacklist():
    try:
        df = pd.read_excel("bikes.xlsx", sheet_name="black list")
        blacklist = set(df['user_id'].tolist())  # Сохраняем ID пользователей в виде множества для быстрого поиска
        return blacklist
    except FileNotFoundError:
        return set()  # Если файл не найден, возвращаем пустой список
    except ValueError:
        return set()  # Если лист не найден, возвращаем пустой список


# Глобальная переменная для хранения черного списка
blacklist = load_blacklist()


# Проверка пользователя на наличие в черном списке
def is_user_blacklisted(user_id):
    return user_id in blacklist


def load_booking_data():
    try:
        # Загружаем данные с листа 'bookings'
        df = pd.read_excel("bikes.xlsx", sheet_name="bookings")
        booking_data = {}

        for _, row in df.iterrows():
            bike_name = row['bike_name']
            user_id = row['user_id']  # Предполагается, что у вас есть поле user_id
            start_date = pd.to_datetime(row['start_date'], dayfirst=True).date()
            end_date = pd.to_datetime(row['end_date'], dayfirst=True).date()

            if bike_name not in booking_data:
                booking_data[bike_name] = {}

            if user_id not in booking_data[bike_name]:
                booking_data[bike_name][user_id] = []

            booking_data[bike_name][user_id].append((start_date, end_date))

        return booking_data

    except FileNotFoundError:
        return {}
    except ValueError:
        return {}


# Function to load bike data from Excel
def load_bike_data():
    df = pd.read_excel("bikes.xlsx", sheet_name="bikes")
    booking_data = load_booking_data()

    honda_pcx_bikes = [
        {
            "name": row['name'],
            "description": row['description'],
            "photo": row['photo'],
            "booked_dates": booking_data.get(row['name'], {})
        }
        for _, row in df.iterrows() if row['model'] == 'Honda PCX'
    ]

    honda_click_bikes = [
        {
            "name": row['name'],
            "description": row['description'],
            "photo": row['photo'],
            "booked_dates": booking_data.get(row['name'], {})
        }
        for _, row in df.iterrows() if row['model'] == 'Honda Click'
    ]

    honda_adv_bikes = [
        {
            "name": row['name'],
            "description": row['description'],
            "photo": row['photo'],
            "booked_dates": booking_data.get(row['name'], {})
        }
        for _, row in df.iterrows() if row['model'] == 'Honda ADV'
    ]

    honda_forza_bikes = [
        {
            "name": row['name'],
            "description": row['description'],
            "photo": row['photo'],
            "booked_dates": booking_data.get(row['name'], {})
        }
        for _, row in df.iterrows() if row['model'] == 'Honda Forza'
    ]

    yamaha_xmax_bikes = [
        {
            "name": row['name'],
            "description": row['description'],
            "photo": row['photo'],
            "booked_dates": booking_data.get(row['name'], {})
        }
        for _, row in df.iterrows() if row['model'] == 'Yamaha Xmax'
    ]

    honda_scoopy_bikes = [
        {
            "name": row['name'],
            "description": row['description'],
            "photo": row['photo'],
            "booked_dates": booking_data.get(row['name'], {})
        }
        for _, row in df.iterrows() if row['model'] == 'Honda Scoopy'
    ]

    honda_zoomer_bikes = [
        {
            "name": row['name'],
            "description": row['description'],
            "photo": row['photo'],
            "booked_dates": booking_data.get(row['name'], {})
        }
        for _, row in df.iterrows() if row['model'] == 'Honda Zoomer'
    ]

    yamaha_fino_bikes = [
        {
            "name": row['name'],
            "description": row['description'],
            "photo": row['photo'],
            "booked_dates": booking_data.get(row['name'], {})
        }
        for _, row in df.iterrows() if row['model'] == 'Yamaha Fino'
    ]

    return honda_pcx_bikes, honda_click_bikes, honda_adv_bikes, honda_forza_bikes, yamaha_xmax_bikes, honda_scoopy_bikes, honda_zoomer_bikes, yamaha_fino_bikes


honda_pcx_bikes, honda_click_bikes, honda_adv_bikes, honda_forza_bikes, yamaha_xmax_bikes, honda_scoopy_bikes, honda_zoomer_bikes, yamaha_fino_bikes = load_bike_data()
print('BIKE', honda_pcx_bikes)


# Save booking data to Excel
def save_booking_data(user_id, bike_name, start_date, end_date, username):
    try:
        # Чтение существующих данных с листа 'bookings'
        existing_data = pd.read_excel("bikes.xlsx", sheet_name="bookings")
    except FileNotFoundError:
        # Если файла не существует, создаем новый DataFrame
        existing_data = pd.DataFrame()
    except ValueError:
        # Если листа 'bookings' не существует, создаем новый DataFrame
        existing_data = pd.DataFrame()

        # Преобразование новых данных в DataFrame
    new_df = pd.DataFrame({
        'user_id': [user_id],
        'bike_name': [bike_name],
        'start_date': [start_date.strftime('%d-%m-%Y')],
        'end_date': [end_date.strftime('%d-%m-%Y')],
        'username': [username]
    })

    # Объединение существующих данных с новыми
    print("new_df", new_df)
    combined_data = pd.concat([existing_data, new_df], ignore_index=True)
    print("DF", combined_data)

    # Запись объединенных данных обратно на лист 'bookings'
    with pd.ExcelWriter("bikes.xlsx", mode="a", if_sheet_exists="replace") as writer:
        combined_data.to_excel(writer, sheet_name="bookings", index=False)


async def send_notification(user_id, end_date_, username):
    # await bot.send_message(user_id, 'ШЕДУЛЕР РАБОТАЕТ')
    user_link = f"https://t.me/{username}"
    booking_info = f"Ваша аренда заканчивается {end_date_}"
    booking_info_admin = f"У пользователя {user_link} аренда заканчивается {end_date_}"
    await bot.send_message(user_id, booking_info)
    await bot.send_message(ADMIN_GROUP_ID, booking_info_admin)
    # for user_id in user_data:
    #     end_date_ = user_data[user_id]['end_date']
    #     print(
    #         f"Отправлено уведомление пользователю {user_id}: Ваша аренда заканчивается {end_date_.strftime('%d-%m-%Y')}")
    #     booking_info = f"Ваша аренда заканчивается {end_date_.strftime('%d-%m-%Y')}"
    #     booking_info_admin = f"У пользователя {user_id} заканчивается аренда {end_date_.strftime('%d-%m-%Y')}"
    #     await bot.send_message(user_id, booking_info)
    #     await bot.send_message(ADMIN_GROUP_ID, booking_info_admin)


async def shedul():
    print("XXX")
    # reminder_date = datetime(2024, 8, 18).date()
    # reminder_time = time(16, 6)
    # reminder_datetime = datetime.combine(reminder_date, reminder_time)
    # reminder_datetime = end_date_ - timedelta(days=1)

    sched = AsyncIOScheduler()
    # Загружаем данные с листа 'bookings'
    df = pd.read_excel("bikes.xlsx", sheet_name="bookings")
    # print("SHEDUL_USER_DATA", user_data)
    for index, row in df.iterrows():
        end_date_ = row['end_date']
        user_id = row['user_id']
        username = row['username']
        end_date_str = datetime.strptime(end_date_, '%d-%m-%Y').date()
        # print('SHEDUL:', index, row)
        reminder_datetime = end_date_str - timedelta(days=1)
        # reminder_date = datetime(2024, 8, 16).date()
        # reminder_time = time(9, 36)
        # reminder_datetime = datetime.combine(reminder_date, reminder_time)

        sched.add_job(
            send_notification,
            trigger='date',
            run_date=reminder_datetime,
            args=[user_id, end_date_, username]
        )
    sched.start()


# Стартовая клавиатура
def start_keyboard(user_id):
    # Загружаем данные с листа 'bookings'
    df = pd.read_excel("bikes.xlsx", sheet_name="bookings")
    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text="🛵 Байки", callback_data="байки"))
    markup.add(InlineKeyboardButton(text="🛡 Условия аренды", callback_data="условия"))
    markup.add(InlineKeyboardButton(text="📞 Контакты", callback_data="контакты"))
    markup.add(InlineKeyboardButton(text="🏆 Отзывы о нас", callback_data="отзывы"))
    if user_id in list(df.user_id.unique()):
        markup.add(InlineKeyboardButton(text="📋 Мои бронирования", callback_data="📋 Мои бронирования"))
    return markup.adjust(1).as_markup()

def bikes_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Honda PCX", callback_data="bikes_pcx_0"),
         InlineKeyboardButton(text="Honda Click", callback_data="bikes_click_0")],
        [InlineKeyboardButton(text="Honda ADV", callback_data="bikes_adv_0"),
         InlineKeyboardButton(text="Honda Forza", callback_data="bikes_forza_0")],
        [InlineKeyboardButton(text="Yamaha Xmax", callback_data="bikes_xmax_0"),
         InlineKeyboardButton(text="Honda Scoopy", callback_data="bikes_scoopy_0")],
        [InlineKeyboardButton(text="Honda Zoomer", callback_data="bikes_zoomer_0"),
         InlineKeyboardButton(text="Yamaha Fino/Grand Filano", callback_data="bikes_fino_0")],
        [InlineKeyboardButton(text="🏠 На главную", callback_data="главная")]
    ])
    return keyboard


def glavnaya_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 На главную",
                              callback_data="главная_2")]
    ])
    return keyboard


# Клавиатура отзывов
def feedback_keyboard():
    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text="✍️ Оставить отзыв", callback_data="оставить_отзыв"))
    markup.add(InlineKeyboardButton(text="📖 Посмотреть отзывы", url=f"t.me/{REVIEWS_GROUP_LINK}"))
    markup.add(InlineKeyboardButton(text="🏠 На главную", callback_data="главная_2"))
    return markup.adjust(1).as_markup()


# Определение состояний
class FeedbackStates(StatesGroup):
    writing_feedback = State()


# Кнопка '🏆 Отзывы о нас'
@dp.callback_query(F.data == 'отзывы')
async def feedback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # Проверка черного списка
    if is_user_blacklisted(user_id):
        await callback_query.message.answer("Вам запрещен доступ к этому боту.")
        return
    photo = FSInputFile("Phangan.jpeg")
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=photo, caption="Выберите действие:"),
        reply_markup=feedback_keyboard())


# Кнопка "✍️ Оставить отзыв"
@dp.callback_query(F.data == 'оставить_отзыв')
async def feedback(callback_query: types.CallbackQuery, state: FSMContext):
    photo = FSInputFile("Phangan.jpeg")
    await callback_query.message.answer("Пожалуйста, напишите свой отзыв:")
    await state.set_state(FeedbackStates.writing_feedback)
    await callback_query.answer()


# Оставить отзыв
@dp.message(FeedbackStates.writing_feedback)
async def collect_review(message: types.Message, state: FSMContext):
    # Сохраняем информацию о сообщении
    user_message_id = message.message_id
    chat_id = message.chat.id
    # Пересылаем сообщение в группу
    await bot.forward_message(
        chat_id=REVIEWS_GROUP_ID,
        from_chat_id=chat_id,
        message_id=user_message_id
    )

    await message.answer(text="Спасибо за ваш отзыв!", reply_markup=glavnaya_keyboard())
    await state.clear()


# Фабрика Callback'ов
class DayCallBack(CallbackData, prefix="day"):
    action: str
    model: str
    page: int
    year: int
    month: int
    day: int


class StartCalendarCallBack(CallbackData, prefix="start_calendar"):
    model: str
    page: int


class EndCalendarCallBack(CallbackData, prefix="end_calendar"):
    model: str
    page: int


class PreMonthCallBack(CallbackData, prefix="Pre_Month"):
    action: str
    model: str
    page: int
    year: int
    month: int


class NexMonthCallBack(CallbackData, prefix="Nex_Month"):
    action: str
    model: str
    page: int
    year: int
    month: int


class ChangeBookingCallBack(CallbackData, prefix="change_booking"):
    model: str
    page: int


class ConfirmCallBack(CallbackData, prefix="confirm_start"):
    action: str
    model: str
    page: int
    year: int
    month: int
    day: int


class ConfirmEndCallBack(CallbackData, prefix="confirm_end"):
    action: str
    model: str
    page: int
    year: int
    month: int
    day: int


class ConfirmBookingCallBack(CallbackData, prefix="confirm_book"):
    action: str
    model: str
    page: int
    year: int
    month: int
    day: int


class BookingInformationCallBack(CallbackData, prefix="booking_information"):
    model: str
    page: int


# Фунция получения байка по модели и странице
def get_bike(model: str, page: int):
    bike_collections = {
        "pcx": honda_pcx_bikes,
        "click": honda_click_bikes,
        "adv": honda_adv_bikes,
        "forza": honda_forza_bikes,
        "xmax": yamaha_xmax_bikes,
        "scoopy": honda_scoopy_bikes,
        "zoomer": honda_zoomer_bikes,
        "fino": yamaha_fino_bikes,
    }

    bikes = bike_collections.get(model)
    if bikes and 0 <= page < len(bikes):
        return bikes[page]


# Клавиатура байка
def bike_keyboard(model: str, page: int):
    bike_collections = {
        "pcx": honda_pcx_bikes,
        "click": honda_click_bikes,
        "adv": honda_adv_bikes,
        "forza": honda_forza_bikes,
        "xmax": yamaha_xmax_bikes,
        "scoopy": honda_scoopy_bikes,
        "zoomer": honda_zoomer_bikes,
        "fino": yamaha_fino_bikes,
    }
    bikes = bike_collections.get(model)
    total_pages = len(bikes) if bikes else 0
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text="🔍 Выбрать даты", callback_data=StartCalendarCallBack(model=model, page=page).pack()))
    keyboard.add(InlineKeyboardButton(text="🛵 Байки", callback_data="байки"))
    keyboard.add(InlineKeyboardButton(text="🏠 На главную", callback_data="главная"))
    if page > 0:
        keyboard.add(InlineKeyboardButton(text="⬅️", callback_data=f"prev_{model}_{page}"))

    keyboard.add(
        InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))

    if bikes and page < total_pages - 1:
        keyboard.add(InlineKeyboardButton(text="➡️", callback_data=f"next_{model}_{page}"))

    return keyboard.adjust(2, 1, 3).as_markup()


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id

    # Проверка черного списка
    if is_user_blacklisted(user_id):
        await message.answer("Вам запрещен доступ к этому боту.")
        return
    photo = FSInputFile("Phangan.jpeg")
    await message.answer_photo(photo=photo, caption="Добро пожаловать в прокат байков 'Essentials Phangan'! "
                                                    "\n\nЭтот бот поможет подобрать байк под ваши потребности и бюджет!"
                               ,
                               reply_markup=start_keyboard(user_id))


# Обработчик кнопки 'байки'
@dp.callback_query(F.data == 'байки')
async def bike_choose(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # Проверка черного списка
    if is_user_blacklisted(user_id):
        await callback_query.message.answer("Вам запрещен доступ к этому боту.")
        return
    photo = FSInputFile("Phangan.jpeg")
    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=photo, caption="🛵 Какую модель байка желаете выбрать?"),
        reply_markup=bikes_keyboard())


# Берем модель и страницу байка
@dp.callback_query(F.data.startswith("bikes_"))
async def show_bike(callback_query: types.CallbackQuery):
    _, model, page = callback_query.data.split("_")
    page = int(page)
    bike = get_bike(model, page)
    photo = FSInputFile(bike["photo"])
    caption = f"{bike['name']}:\n\n{bike['description']}"

    await callback_query.message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=bike_keyboard(model, page)
    )


# Пагинация байков
@dp.callback_query(F.data.startswith(("prev_", "next_")))
async def paginate_bikes(callback_query: types.CallbackQuery):
    data = callback_query.data
    action, model, current_page = data.split("_")
    current_page = int(current_page)
    if action == "prev":
        next_page = current_page - 1 if current_page > 0 else 0
    else:
        next_page = current_page if model not in ["pcx", "click", "adv", "forza", "xmax", "scoopy", "zoomer",
                                                  "fino"] or current_page >= len(
            get_bike(model=model, page=0)) + len(get_bike(model=model, page=0)) else current_page + 1

    bike = get_bike(model, next_page)
    photo = FSInputFile(bike["photo"])
    caption = f"{bike['name']}:\n\n{bike['description']}"

    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=photo, caption=caption),
        reply_markup=bike_keyboard(model, next_page)
    )


# Обработчик кнопки '🏠 На главную'
@dp.callback_query(F.data == "главная")
async def main_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    photo = FSInputFile("Phangan.jpeg")
    await callback_query.message.edit_media(
        types.InputMediaPhoto(media=photo, caption="Добро пожаловать в прокат байков 'Essentials Phangan'! "
                                                   "\n\nЭтот бот поможет подобрать байк под ваши потребности и бюджет!"),
        reply_markup=start_keyboard(user_id)
    )


# Функция создания клавиатуры календаря
def create_calendar_keyboard(year: int, month: int, action: str, model: str, page: int, bike_name: str):
    # Загружаем актуальные данные о бронированиях
    booking_data = load_booking_data()
    # Получаем даты, которые уже забронированы для конкретного байка
    booked_dates = booking_data.get(bike_name, {})
    markup = InlineKeyboardBuilder()
    month_name = datetime(year, month, day=1).strftime('%B %Y')
    markup.add(InlineKeyboardButton(text="🏠 На главную", callback_data="главная_2"))
    markup.add(InlineKeyboardButton(text=month_name, callback_data="ignore"))

    markup.add(
        *[InlineKeyboardButton(text=day, callback_data="ignore") for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]])
    month_calendar = calendar.monthcalendar(year, month)
    print("X1337", booked_dates)
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                booked = False
                if booked_dates:
                    for i in booked_dates.values():
                        for interval_start, interval_end in i:

                            if str(interval_start) <= date_str <= str(interval_end):
                                row.append(InlineKeyboardButton(text=f"✖️{day}", callback_data="ignore"))
                                booked = True
                                break
                if not booked:
                    row.append(InlineKeyboardButton(text=str(day),
                                                    callback_data=DayCallBack(action=action, model=model,
                                                                              page=page, year=year,
                                                                              month=month,
                                                                              day=day).pack()))
        markup.add(*row)
    markup.add(*[InlineKeyboardButton(text="⬅️",
                                      callback_data=PreMonthCallBack(action=action, model=model,
                                                                     page=page, year=year,
                                                                     month=month).pack()), InlineKeyboardButton(
        text="➡️",
        callback_data=NexMonthCallBack(action=action, model=model,
                                       page=page, year=year,
                                       month=month).pack())])
    return markup.adjust(1, 1, 7, 7, 7, 7, 7, 7, 7).as_markup()


# Обработчик выбора даты начала бронирования
@dp.callback_query(StartCalendarCallBack.filter())
async def show_start_calendar(callback_query: types.CallbackQuery, callback_data: StartCalendarCallBack):
    model = callback_data.model
    page = callback_data.page
    now = datetime.now()
    bike = get_bike(model, page)
    booked_dates = bike["booked_dates"]
    await callback_query.message.answer(
        text=f"Сегодняшняя дата: {date.today()} \n\nПожалуйста, выберите дату начала бронирования:",
        reply_markup=create_calendar_keyboard(year=now.year, month=now.month,
                                              action="start", model=model,
                                              page=page, bike_name=bike['name']))


# Обработчик выбора даты окончания бронирования
@dp.callback_query(EndCalendarCallBack.filter())
async def show_end_calendar(callback_query: types.CallbackQuery, callback_data: EndCalendarCallBack):
    model = callback_data.model
    page = callback_data.page
    now = datetime.now()
    bike = get_bike(model, page)
    booked_dates = bike["booked_dates"]
    await callback_query.message.edit_text(text="Пожалуйста, выберите дату окончания бронирования:",
                                           reply_markup=create_calendar_keyboard(year=now.year, month=now.month,
                                                                                 action="end", model=model,
                                                                                 page=page,
                                                                                 bike_name=bike['name']))


# Проверка на пересечение интервалов брони
def is_date_range_available(start_date, end_date, bike_name):
    # Загружаем актуальные данные о бронированиях
    booking_data = load_booking_data()
    # Получаем даты, которые уже забронированы для конкретного байка
    booked_dates = booking_data.get(bike_name, {})
    for i in booked_dates.values():
        for interval_start, interval_end in i:
            if start_date <= interval_end and end_date >= interval_start:
                return False
    return True


# Клавиатура подтверждения даты начала
def confirm_date(year: int, month: int, action: str, model: str, page: int, day: int,
                 booked_dates: dict):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data=ConfirmCallBack(action=action, model=model,
                                                                                page=page, year=year,
                                                                                month=month,
                                                                                day=day).pack())],
        [InlineKeyboardButton(text="Назад", callback_data=StartCalendarCallBack(model=model, page=page).pack())]
    ])
    return keyboard


# Клавиатура подтверждения даты окончания
def confirm_end_date(year: int, month: int, action: str, model: str, page: int, day: int,
                     booked_dates: dict):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить", callback_data=ConfirmEndCallBack(action=action, model=model,
                                                                                   page=page, year=year,
                                                                                   month=month,
                                                                                   day=day).pack())],
        [InlineKeyboardButton(text="Назад", callback_data=EndCalendarCallBack(model=model, page=page).pack())]
    ])
    return keyboard


# Обработчик выбора конкретного дня в календаре
@dp.callback_query(DayCallBack.filter())
async def process_calendar_day(callback_query: types.CallbackQuery, callback_data: DayCallBack):
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day
    action = callback_data.action
    page = callback_data.page
    model = callback_data.model
    bike = get_bike(model, page)
    booked_dates = bike["booked_dates"]
    selected_date = date(year, month, day)
    user_id = callback_query.from_user.id

    if action == "start":
        if selected_date < datetime.now().date():
            await callback_query.message.answer(
                "Дата начала бронирования не может быть раньше текущей даты. Выберите другую дату.")
        else:
            user_data[user_id] = {"start_date": selected_date}
            await callback_query.message.edit_text(
                text=f"Дата начала бронирования: {selected_date.strftime('%d-%m-%Y')}",
                reply_markup=confirm_date(year=selected_date.year, month=selected_date.month, action="end",
                                          model=model,
                                          page=page, day=day, booked_dates=booked_dates))

    elif action == "end":
        if user_id in user_data and "start_date" in user_data[user_id]:
            start_date = user_data[user_id]["start_date"]
            if selected_date < start_date:
                await callback_query.message.answer(
                    "Дата окончания бронирования не может быть раньше даты начала. Пожалуйста, выберите дату окончания снова.")
                return
            # Check if the entire date range is available
            if not is_date_range_available(start_date, selected_date, bike_name=bike['name']):
                await callback_query.message.answer(
                    "Этот интервал дат уже забронирован. Пожалуйста, выберите другой интервал.")
                await callback_query.message.answer(
                    text=f"Сегодняшняя дата: {date.today()} \n\nПожалуйста, выберите дату начала бронирования:",
                    reply_markup=create_calendar_keyboard(year=year, month=month,
                                                          action="start", model=model,
                                                          page=page, bike_name=bike['name']))
            else:
                await callback_query.message.edit_text(
                    text=f"Дата окончания бронирования: {selected_date.strftime('%d-%m-%Y')}",
                    reply_markup=confirm_end_date(year=selected_date.year, month=selected_date.month, action="end",
                                                  model=model,
                                                  page=page, day=day, booked_dates=booked_dates))
        else:
            await callback_query.message.answer("Пожалуйста, сначала выберите дату начала бронирования.")


# Обработчик пролистывания календаря назад
@dp.callback_query(PreMonthCallBack.filter())
async def prev_month(callback_query: types.CallbackQuery, callback_data: PreMonthCallBack):
    year = callback_data.year
    month = callback_data.month
    action = callback_data.action
    page = callback_data.page
    model = callback_data.model
    bike = get_bike(model, page)
    booked_dates = bike["booked_dates"]
    current_date = datetime(int(year), int(month), day=1)
    prev_date = current_date - timedelta(days=1)
    await callback_query.message.edit_reply_markup(
        reply_markup=create_calendar_keyboard(year=prev_date.year, month=prev_date.month, action=action,
                                              model=model,
                                              page=int(page),
                                              bike_name=bike['name']))


# Обработчик пролистывания календаря вперед
@dp.callback_query(NexMonthCallBack.filter())
async def next_month(callback_query: types.CallbackQuery, callback_data: NexMonthCallBack):
    year = callback_data.year
    month = callback_data.month
    action = callback_data.action
    page = callback_data.page
    model = callback_data.model
    bike = get_bike(model, page)
    booked_dates = bike["booked_dates"]
    current_date = datetime(int(year), int(month), day=1)
    next_date = current_date + timedelta(days=31)
    next_date = next_date.replace(day=1)
    await callback_query.message.edit_reply_markup(
        reply_markup=create_calendar_keyboard(year=next_date.year, month=next_date.month, action=action,
                                              model=model,
                                              page=int(page),
                                              bike_name=bike['name']))


# Обработчик кнопки "На главную"
@dp.callback_query(F.data == "главная_2")
async def glavnaya_welcome(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    photo = FSInputFile("Phangan.jpeg")
    await callback_query.message.answer_photo(photo=photo,
                                              caption="Добро пожаловать в прокат байков 'Essentials Phangan'! "
                                                      "\n\nЭтот бот поможет подобрать байк под ваши потребности и бюджет!"
                                              ,
                                              reply_markup=start_keyboard(user_id))


# Функция создания клавиатуры выбора даты
def date_keyboard(action: str, model: str, page: int, year: int, month: int, day: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить даты",
                              callback_data=ChangeBookingCallBack(model=model, page=page).pack())],
        [InlineKeyboardButton(text="Подтвердить бронирование",
                              callback_data=ConfirmBookingCallBack(year=year, month=month,
                                                                   action=action,
                                                                   model=model,
                                                                   page=page, day=day).pack())],
        [InlineKeyboardButton(text="🏠 На главную", callback_data="главная_2")],
    ])
    return keyboard


# Обработчик кнопки "Изменить даты"
@dp.callback_query(ChangeBookingCallBack.filter())
async def change_booking(callback_query: types.CallbackQuery, callback_data: ChangeBookingCallBack):
    model = callback_data.model
    page = callback_data.page
    bike = get_bike(model, page)
    user_id = callback_query.from_user.id

    if user_id in bike["booked_dates"]:
        del bike["booked_dates"][user_id]  # Сброс забронированных дат для данного пользователя

    await callback_query.message.edit_text(
        text="Выберите новые даты: ",
        reply_markup=create_calendar_keyboard(datetime.now().year, datetime.now().month, "start", model, page,
                                              bike["booked_dates"])
    )


# Обработчик кнопки "Подтвердить" даты начала бронирования
@dp.callback_query(ConfirmCallBack.filter())
async def confirm_start(callback_query: types.CallbackQuery, callback_data: ConfirmCallBack):
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day
    page = callback_data.page
    model = callback_data.model
    bike = get_bike(model, page)
    selected_date = date(year, month, day)
    await callback_query.message.edit_text(
        text=f"Дата начала бронирования: {selected_date.strftime('%d-%m-%Y')}\n\nТеперь выберите дату окончания бронирования:",
        reply_markup=create_calendar_keyboard(year=selected_date.year, month=selected_date.month, action="end",
                                              model=model,
                                              page=page, bike_name=bike['name']))


# Обработчик кнопки "Подтвердить" даты окончания бронирования
@dp.callback_query(ConfirmEndCallBack.filter())
async def confirm_end(callback_query: types.CallbackQuery, callback_data: ConfirmEndCallBack):
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day
    action = callback_data.action
    page = callback_data.page
    model = callback_data.model
    bike = get_bike(model, page)
    selected_date = date(year, month, day)
    start_date = user_data[callback_query.from_user.id]["start_date"]
    await callback_query.message.edit_text(
        text=f"Выбранные даты: \n\nC {start_date.strftime('%d-%m-%Y')} по {selected_date.strftime('%d-%m-%Y')}!"
        ,
        reply_markup=date_keyboard(action, model, page, year, month, day))


# Клавиатура после окончания бронирования
def booking_information(model, page):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 На главную", callback_data="главная_2")],
        [InlineKeyboardButton(text="📋 Мои бронирования", callback_data="📋 Мои бронирования")], ])
    return keyboard


# Обработчик кнопки "Подтвердить бронирование"
@dp.callback_query(ConfirmBookingCallBack.filter())
async def confirm_booking(callback_query: types.CallbackQuery, callback_data: ConfirmBookingCallBack):
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day
    page = callback_data.page
    model = callback_data.model
    bike = get_bike(model, page)
    user_id = callback_query.from_user.id
    start_date = user_data[callback_query.from_user.id]["start_date"]
    selected_date = date(year, month, day)
    booked_dates = bike["booked_dates"]
    user_data[user_id]["end_date"] = selected_date
    bike_name = bike['name']
    user_data[user_id]['bike_name'] = bike_name
    username = callback_query.from_user.username
    print("1337X", booked_dates)
    if user_id in user_data and "start_date" in user_data[user_id] and "end_date" in user_data[user_id]:
        if user_id not in booked_dates:
            booked_dates[user_id] = []
        booke = start_date.strftime('%d-%m-%Y'), selected_date.strftime('%d-%m-%Y')
        booked_dates[user_id].append(booke)
        print("USER_DATA", user_data)
        print("BOOKED_DATES", booked_dates)
        start_date = user_data[user_id]["start_date"]
        end_date = user_data[user_id]["end_date"]
        model = 'pcx'  # или 'click', в зависимости от выбранной модели байка
        page = 0  # номер страницы, на которой выбран байк
        # Получение ссылки на профиль пользователя
        user_profile_link = f"https://t.me/{callback_query.from_user.username}" if callback_query.from_user.username else "Не задано"

        # Отправка сообщения администраторам
        booking_info = (
            f"Пользователь {callback_query.from_user.full_name} ({user_profile_link}) \n\n"
            f"забронировал {user_data[user_id]['bike_name']} \nс {start_date.strftime('%d-%m-%Y')} по {end_date.strftime('%d-%m-%Y')}."
        )
        save_booking_data(user_id, bike['name'], start_date, end_date, username)
        await bot.send_message(ADMIN_GROUP_ID, booking_info)

        await callback_query.message.edit_text(
            text="Ваше бронирование подтверждено!\n\nС вами свяжутся Админы в ближайшее время!",
            reply_markup=booking_information(model, page))
        reminder_date = datetime(2024, 7, 31).date()
        reminder_time = time(0, 0)  # Время напоминания (14:30)
        reminder_datetime = datetime.combine(reminder_date, reminder_time)
        # Schedule a notification at the specified time
        # scheduler.add_job(send_notification(user_id), trigger='date', run_date=reminder_datetime,
        #                 args=[user_id, end_date])
    else:
        await callback_query.message.answer("Произошла ошибка при бронировании. Попробуйте снова.")


# Обработчик кнопки "📋 Мои бронирования"
@dp.callback_query(F.data == "📋 Мои бронирования")
async def my_bookings(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        # Загружаем данные с листа 'bookings'
        df = pd.read_excel("bikes.xlsx", sheet_name="bookings")

        # Фильтруем бронирования по user_id
        user_bookings = df[df['user_id'] == user_id]

        if not user_bookings.empty:
            booking_info = "Ваши бронирования:\n"
            for i, row in user_bookings.iterrows():
                bike_name = row['bike_name']
                start_date = pd.to_datetime(row['start_date'], dayfirst=True).strftime('%d-%m-%Y')
                end_date = pd.to_datetime(row['end_date'], dayfirst=True).strftime('%d-%m-%Y')
                booking_info += f"{i + 1}. {bike_name} с {start_date} по {end_date}\n"
        else:
            booking_info = "У вас нет текущих бронирований."

    except FileNotFoundError:
        booking_info = "Ошибка: Файл с данными о бронированиях не найден."
    except ValueError:
        booking_info = "Ошибка: Неверный формат данных в файле бронирований."

    await callback_query.message.answer(text=booking_info, reply_markup=glavnaya_keyboard())


# Обработчик кнопки "Условия аренды"
@dp.callback_query(F.data == "условия")
async def rent_terms(callback_query: types.CallbackQuery):
    photo = FSInputFile("Phangan.jpeg")
    await callback_query.message.answer(

        text="1️⃣ Документы: При аренде байка необходимо предоставить оригинал загранпаспорта или другого удостоверяющего личность документа."
             "\n2️⃣ Депозит: Обязателен денежный депозит, размер которого зависит от модели байка."
             "\n3️⃣ Срок аренды: Минимальный срок аренды составляет трое суток."
             "\n4️⃣ Оплата: Оплата производится заранее, при получении байка."
             "\n5️⃣ Возврат байка: Байк должен быть возвращен в оговоренное время и место в том же состоянии, в каком он был получен."
             "\nВ случае задержки возврата арендатор оплачивает дополнительное время согласно тарифам."
             "\n6️⃣ Техническое обслуживание и использование: Арендатор обязуется следить за техническим состоянием байка и немедленно сообщать о любых неисправностях."
             "\n7️⃣ Ответственность арендатора: Арендатор несет ответственность за любой ущерб, причиненный байку по его вине."
             "\n В случае утери или повреждения байка арендатор возмещает стоимость ремонта или полной замены."
             "\n 8️⃣ Отмена и изменение бронирования: Отмена бронирования возможна не позднее чем за 24 часа до начала аренды без штрафов."
             "\n В случае отмены менее чем за 24 часа до начала аренды взимается штраф в размере 50% от стоимости аренды.",
        reply_markup=glavnaya_keyboard()

    )


# Обработчик кнопки "Контакты"
@dp.callback_query(F.data == "контакты")
async def contacts(callback_query: types.CallbackQuery):
    await callback_query.message.answer_contact(phone_number='+79877432071',  # Замените на ваш номер телефона
                                                first_name='Alex',  # Замените на ваше имя
                                                last_name='Tentser'  # Замените на вашу фамилию (необязательно)
                                                )
    await callback_query.message.answer_contact(phone_number='+79202523959',  # Замените на ваш номер телефона
                                                first_name='Dmitriy',  # Замените на ваше имя
                                                last_name='Sbitnev'  # Замените на вашу фамилию (необязательно)
                                                , reply_markup=glavnaya_keyboard())
    await callback_query.answer()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await shedul()
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
