from aiogram import Bot, Dispatcher, types
import asyncio
from aiogram.filters import Command
from aiogram import F
import logging
from aiogram.types import FSInputFile
from aiogram.filters.callback_data import CallbackData
from datetime import datetime, timedelta, date, time
import calendar
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TOKEN
import asyncpg
import psycopg2


logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Данные для подключения к базе данных
DATABASE_URL = "postgresql://postgres:HCXoXLARQwqBOJofbfPkZXEepCdtuNWm@junction.proxy.rlwy.net:31130/railway"  # URL подключения к базе данных из Railway


# Функция для подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        return conn
    except Exception as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        raise


# Функция для загрузки данных о бронированиях из таблицы "bookings"
def load_booking_data():
    conn = get_db_connection()
    try:
        query = "SELECT bike_name, user_id, start_date, end_date FROM bookings"
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        booking_data = {}

        for row in rows:
            bike_name = row[0]
            user_id = row[1]
            start_date = row[2]
            end_date = row[3]

            if bike_name not in booking_data:
                booking_data[bike_name] = {}

            if user_id not in booking_data[bike_name]:
                booking_data[bike_name][user_id] = []

            booking_data[bike_name][user_id].append((start_date, end_date))

        return booking_data
    finally:
        conn.close()


# Функция для загрузки данных о байках из таблицы "bikes"
def load_bike_data():
    conn = get_db_connection()
    booking_data = load_booking_data()

    try:
        cursor = conn.cursor()
        query = "SELECT name, description, photo, model FROM bikes"
        cursor.execute(query)
        rows = cursor.fetchall()

        honda_pcx_bikes = [
            {
                "name": row[0],  # Используем индексы вместо имен полей
                "description": row[1],
                "photo": row[2],
                "booked_dates": booking_data.get(row[0], {})
            }
            for row in rows if row[3] == 'pcx'
        ]

        honda_click_bikes = [
            {
                "name": row[0],  # Используем индексы вместо имен полей
                "description": row[1],
                "photo": row[2],
                "booked_dates": booking_data.get(row[0], {})
            }
            for row in rows if row[3] == 'click'
        ]

        honda_adv_bikes = [
            {
                "name": row[0],  # Используем индексы вместо имен полей
                "description": row[1],
                "photo": row[2],
                "booked_dates": booking_data.get(row[0], {})
            }
            for row in rows if row[3] == 'adv'
        ]

        honda_forza_bikes = [
            {
                "name": row[0],  # Используем индексы вместо имен полей
                "description": row[1],
                "photo": row[2],
                "booked_dates": booking_data.get(row[0], {})
            }
            for row in rows if row[3] == 'forza'
        ]

        yamaha_xmax_bikes = [
            {
                "name": row[0],  # Используем индексы вместо имен полей
                "description": row[1],
                "photo": row[2],
                "booked_dates": booking_data.get(row[0], {})
            }
            for row in rows if row[3] == 'xmax'
        ]

        honda_scoopy_bikes = [
            {
                "name": row[0],  # Используем индексы вместо имен полей
                "description": row[1],
                "photo": row[2],
                "booked_dates": booking_data.get(row[0], {})
            }
            for row in rows if row[3] == 'scoopy'
        ]

        honda_zoomer_bikes = [
            {
                "name": row[0],  # Используем индексы вместо имен полей
                "description": row[1],
                "photo": row[2],
                "booked_dates": booking_data.get(row[0], {})
            }
            for row in rows if row[3] == 'zoomer'
        ]

        yamaha_fino_bikes = [
            {
                "name": row[0],  # Используем индексы вместо имен полей
                "description": row[1],
                "photo": row[2],
                "booked_dates": booking_data.get(row[0], {})
            }
            for row in rows if row[3] == 'fino'
        ]


        return honda_pcx_bikes, honda_click_bikes, honda_adv_bikes, honda_forza_bikes, yamaha_xmax_bikes, honda_scoopy_bikes, honda_zoomer_bikes, yamaha_fino_bikes
    finally:
        conn.close()


honda_pcx_bikes, honda_click_bikes, honda_adv_bikes, honda_forza_bikes, yamaha_xmax_bikes, honda_scoopy_bikes, honda_zoomer_bikes, yamaha_fino_bikes = load_bike_data()


# Функция для сохранения данных о бронировании в таблицу "bookings"
def save_booking_data(user_id, bike_name, start_date, end_date, username):
    conn = get_db_connection()
    cursor = None
    try:
        cursor = conn.cursor()  # Создание курсора для выполнения SQL-запросов
        query = """
            INSERT INTO bookings (user_id, bike_name, start_date, end_date, username)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, bike_name, start_date, end_date, username))  # Выполнение запроса через курсор
        conn.commit()  # Сохранение изменений в базе данных
        print("Бронирование успешно сохранено в базу данных.")
    except Exception as e:
        print(f"Ошибка при сохранении данных: {e}")
    finally:
        if cursor:
            cursor.close()  # Закрытие курсора, если он был создан
        conn.close()  # Закрытие соединения


user_data = {}
# {519275422: {'start_date': datetime.date(2024, 8, 15), 'end_date': datetime.date(2024, 8, 18), 'bike_name': 'Honda PCX 1'}}

ADMIN_GROUP_ID = -4582383727

REVIEWS_GROUP_ID = -4268299607

REVIEWS_GROUP_LINK = '+fnrHSRyfk-A5ZmQy'


# Функция для загрузки черного списка из базы данных
def load_blacklist():
    try:
        # Получаем соединение с базой данных через существующую функцию
        conn = get_db_connection()

        # Создаем курсор для выполнения запросов
        cursor = conn.cursor()

        # Выполняем запрос для получения черного списка пользователей
        query = "SELECT user_id FROM blacklist;"
        cursor.execute(query)

        # Извлекаем результаты и создаем множество user_id
        records = cursor.fetchall()
        blacklist = {record[0] for record in records}  # Предполагается, что user_id в первой колонке

        # Закрываем курсор и соединение
        cursor.close()
        conn.close()

        # Возвращаем множество с ID пользователей в черном списке
        return blacklist

    except (psycopg2.DatabaseError, Exception) as e:
        # Логируем ошибку при возникновении проблемы с базой данных
        logging.error(f"Ошибка при загрузке черного списка: {e}")
        return set()  # Возвращаем пустое множество в случае ошибки


async def send_notification(user_id, end_date_, username):
    user_link = f"https://t.me/{username}"
    booking_info = f"Ваша аренда заканчивается {end_date_}"
    booking_info_admin = f"У пользователя {user_link} аренда заканчивается {end_date_}"
    await bot.send_message(user_id, booking_info)
    await bot.send_message(ADMIN_GROUP_ID, booking_info_admin)


# Асинхронная функция для планирования задач
async def shedul():
    sched = AsyncIOScheduler()
    conn = None  # Инициализация переменной conn

    try:
        # Получаем соединение с базой данных
        conn = await asyncpg.connect(DATABASE_URL)

        # Выполняем запрос для получения данных бронирования
        query = "SELECT end_date, user_id, username FROM bookings;"
        rows = await conn.fetch(query)

        # Обрабатываем каждую строку результата
        for row in rows:
            end_date_ = row['end_date']
            user_id = row['user_id']
            username = row['username']

            # Преобразуем дату окончания в нужный формат
            if isinstance(end_date_, str):
                end_date_ = datetime.strptime(end_date_, '%d-%m-%Y').date()

            reminder_time = time(8, 44)

            reminder_datetime = datetime.combine(datetime.now().date(), reminder_time)

            # Добавляем задачу в планировщик
            sched.add_job(
                send_notification,
                trigger='date',
                run_date=reminder_datetime,
                args=[user_id, end_date_, username]
            )

        # Запускаем планировщик
        sched.start()

    except Exception as e:
        logging.error(f"Ошибка при планировании задач: {e}")

    finally:
        # Закрываем соединение с базой данных
        await conn.close()


def get_user_ids_from_db():
    # Подключаемся к базе данных
    conn = psycopg2.connect(DATABASE_URL)
    try:
        # Создаем курсор для выполнения запроса
        cursor = conn.cursor()
        # Выполняем запрос к базе данных, чтобы получить уникальные user_id из таблицы "bookings"
        cursor.execute("SELECT DISTINCT user_id FROM bookings")
        rows = cursor.fetchall()
        # Извлекаем user_id из результатов
        user_ids = {row[0] for row in rows}
        return user_ids
    finally:
        conn.close()


# Стартовая клавиатура
def start_keyboard(user_id):
    # Получаем уникальные user_id из базы данных
    user_ids = get_user_ids_from_db()
    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text="🛵 Байки", callback_data="байки"))
    markup.add(InlineKeyboardButton(text="🛡 Условия аренды", callback_data="условия"))
    markup.add(InlineKeyboardButton(text="📞 Контакты", callback_data="контакты"))
    markup.add(InlineKeyboardButton(text="🏆 Отзывы о нас", callback_data="отзывы"))
    # Проверяем, есть ли user_id среди бронирований
    if user_id in user_ids:
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
    blacklist = load_blacklist()
    # Проверка черного списка
    if user_id in blacklist:
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


# Функция для получения байка по модели и странице
async def get_bike(model: str, page: int):
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


# Клавиатура для управления байком и навигацией по страницам
def bike_keyboard(model: str, page: int):
    conn = get_db_connection()
    cursor = None
    try:
        cursor = conn.cursor()  # Создание курсора

        # Запрос для получения общего количества байков по модели
        query = """
            SELECT COUNT(*) 
            FROM bikes 
            WHERE model = %s
        """
        cursor.execute(query, (model,))  # Выполнение запроса
        result = cursor.fetchone()  # Получение одной строки результата
        total_bikes = result[0] if result else 0
        total_pages = total_bikes  # Расчет общего количества страниц, если 10 байков на страницу

        # Инициализация клавиатуры
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            InlineKeyboardButton(
                text="🔍 Выбрать даты",
                callback_data=StartCalendarCallBack(model=model, page=page).pack()
            )
        )
        keyboard.add(InlineKeyboardButton(text="🛵 Байки", callback_data="байки"))
        keyboard.add(InlineKeyboardButton(text="🏠 На главную", callback_data="главная"))

        # Добавление кнопок навигации по страницам
        if page > 0:
            keyboard.add(InlineKeyboardButton(text="⬅️", callback_data=f"prev_{model}_{page}"))

        keyboard.add(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))

        if page < total_pages - 1:
            keyboard.add(InlineKeyboardButton(text="➡️", callback_data=f"next_{model}_{page}"))

        # Возврат клавиатуры с кнопками
        return keyboard.adjust(2, 1, 3).as_markup()
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
    finally:
        if cursor:
            cursor.close()  # Закрытие курсора
        conn.close()  # Закрытие соединения


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    blacklist = load_blacklist()

    # Проверка черного списка
    if user_id in blacklist:
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
    blacklist = load_blacklist()
    # Проверка черного списка
    if user_id in blacklist:
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
    bike = await get_bike(model, page)
    photo = FSInputFile(bike["photo"])
    caption = f"{bike['name']}:\n\n{bike['description']}"

    await callback_query.message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=bike_keyboard(model, page)
    )


# Функция для получения общего количества байков по модели
def get_total_bikes(model: str) -> int:
    conn = get_db_connection()
    cursor = None
    try:
        cursor = conn.cursor()  # Создание курсора
        query = """
            SELECT COUNT(*) 
            FROM bikes 
            WHERE model = %s
        """
        cursor.execute(query, (model,))  # Выполнение запроса
        result = cursor.fetchone()  # Получение одной строки результата
        total_bikes = result[0] if result else 0  # Извлечение значения из результата
        return total_bikes
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return 0
    finally:
        if cursor:
            cursor.close()  # Закрытие курсора
        conn.close()  # Закрытие соединения


# Пагинация байков
@dp.callback_query(F.data.startswith(("prev_", "next_")))
async def paginate_bikes(callback_query: types.CallbackQuery):
    data = callback_query.data
    action, model, current_page = data.split("_")
    current_page = int(current_page)

    # Определяем номер следующей страницы
    if action == "prev":
        next_page = current_page - 1 if current_page > 0 else 0
    else:
        # Получаем количество байков для проверки на последнюю страницу
        total_bikes = get_total_bikes(
            model)  # Добавьте функцию get_total_bikes, чтобы считать количество байков в модели
        next_page = current_page + 1 if current_page < total_bikes - 1 else current_page

    # Асинхронно получаем данные о байке
    bike = await get_bike(model, next_page)  # Добавлено await для асинхронной функции

    # Проверяем, что байк найден
    if bike:
        # Загружаем фотографию байка
        photo = FSInputFile(bike["photo"])
        caption = f"{bike['name']}:\n\n{bike['description']}"

        # Получаем клавиатуру с использованием await
        keyboard = bike_keyboard(model, next_page)  # Добавлено await для асинхронного вызова

        # Редактируем сообщение с новым байком и клавиатурой
        await callback_query.message.edit_media(
            types.InputMediaPhoto(media=photo, caption=caption),
            reply_markup=keyboard
        )
    else:
        # Обработка случая, когда байк не найден
        await callback_query.message.answer("Байк не найден или отсутствует.")


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
async def create_calendar_keyboard(year: int, month: int, action: str, model: str, page: int, bike_name: str):
    # Загружаем актуальные данные о бронированиях
    booking_data = load_booking_data()
    # Получаем даты, которые уже забронированы для конкретного байка
    booked_dates = booking_data.get(bike_name, {})
    markup = InlineKeyboardBuilder()
    month_name = datetime(year, month, day=1).strftime('%B %Y')
    markup.add(InlineKeyboardButton(text="🏠 На главную", callback_data="главная_2"))
    markup.add(InlineKeyboardButton(text=month_name, callback_data="ignore"))

    # Добавляем названия дней недели
    markup.add(
        *[InlineKeyboardButton(text=day, callback_data="ignore") for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]]
    )

    month_calendar = calendar.monthcalendar(year, month)

    # Заполняем календарь с учетом забронированных дат
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                booked = False
                if booked_dates:
                    for intervals in booked_dates.values():
                        for interval_start, interval_end in intervals:
                            if str(interval_start) <= date_str <= str(interval_end):
                                row.append(InlineKeyboardButton(text=f"✖️{day}", callback_data="ignore"))
                                booked = True
                                break
                if not booked:
                    row.append(
                        InlineKeyboardButton(
                            text=str(day),
                            callback_data=DayCallBack(
                                action=action,
                                model=model,
                                page=page,
                                year=year,
                                month=month,
                                day=day
                            ).pack()
                        )
                    )
        markup.add(*row)

    # Добавляем кнопки навигации по месяцам
    markup.add(
        *[
            InlineKeyboardButton(
                text="⬅️",
                callback_data=PreMonthCallBack(
                    action=action, model=model, page=page, year=year, month=month
                ).pack()
            ),
            InlineKeyboardButton(
                text="➡️",
                callback_data=NexMonthCallBack(
                    action=action, model=model, page=page, year=year, month=month
                ).pack()
            )
        ]
    )

    return markup.adjust(1, 1, 7, 7, 7, 7, 7, 7, 7).as_markup()


# Обработчик выбора даты начала бронирования
@dp.callback_query(StartCalendarCallBack.filter())
async def show_start_calendar(callback_query: types.CallbackQuery, callback_data: StartCalendarCallBack):
    model = callback_data.model
    page = callback_data.page
    now = datetime.now()
    bike = await get_bike(model, page)  # Предполагается, что get_bike теперь асинхронная

    # Используем await для вызова асинхронной функции create_calendar_keyboard
    calendar_keyboard = await create_calendar_keyboard(
        year=now.year,
        month=now.month,
        action="start",
        model=model,
        page=page,
        bike_name=bike['name']
    )

    await callback_query.message.answer(
        text=f"Сегодняшняя дата: {date.today()} \n\nПожалуйста, выберите дату начала бронирования:",
        reply_markup=calendar_keyboard
    )


# Обработчик выбора даты окончания бронирования
@dp.callback_query(EndCalendarCallBack.filter())
async def show_end_calendar(callback_query: types.CallbackQuery, callback_data: EndCalendarCallBack):
    model = callback_data.model
    page = callback_data.page
    now = datetime.now()
    bike = await get_bike(model, page)  # Предполагается, что get_bike теперь асинхронная

    # Используем await для вызова асинхронной функции create_calendar_keyboard
    calendar_keyboard = await create_calendar_keyboard(
        year=now.year,
        month=now.month,
        action="end",
        model=model,
        page=page,
        bike_name=bike['name']
    )

    await callback_query.message.edit_text(
        text="Пожалуйста, выберите дату окончания бронирования:",
        reply_markup=calendar_keyboard
    )


async def create_pool():
    return await asyncpg.create_pool(dsn=DATABASE_URL)


# Проверка на пересечение интервалов брони
async def is_date_range_available(start_date: date, end_date: date, bike_name: str) -> bool:
    """
    Проверяет доступность интервала бронирования для указанного байка.

    :param start_date: Дата начала бронирования.
    :param end_date: Дата окончания бронирования.
    :param bike_name: Имя байка.
    :return: True, если даты доступны, иначе False.
    """
    pool = await create_pool()

    # Запрос к базе данных для получения забронированных интервалов для данного байка
    query = """
    SELECT start_date, end_date
    FROM bookings
    WHERE bike_name = $1;
    """

    async with pool.acquire() as connection:
        records = await connection.fetch(query, bike_name)

    # Проверяем, пересекается ли интервал с существующими бронированиями
    for record in records:
        interval_start = record['start_date']
        interval_end = record['end_date']
        print(f"Проверка интервала: {interval_start} - {interval_end}")

        if start_date <= interval_end and end_date >= interval_start:
            print(f"Пересечение найдено с интервалом: {interval_start} - {interval_end}")
            return False

    print("Даты доступны для бронирования")
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
    bike = await get_bike(model, page)  # Используем асинхронную функцию для получения байка из базы данных
    selected_date = date(year, month, day)
    user_id = callback_query.from_user.id

    if action == "start":
        if selected_date < datetime.now().date():
            await callback_query.message.answer(
                "Дата начала бронирования не может быть раньше текущей даты. Выберите другую дату."
            )
        else:
            user_data[user_id] = {"start_date": selected_date}
            # Проверяем, что функция confirm_date корректно вызывается с await, если она асинхронная
            confirm_markup = confirm_date(  # Добавлено await для асинхронного вызова
                year=selected_date.year,
                month=selected_date.month,
                action="end",
                model=model,
                page=page,
                day=day,
                booked_dates={}  # Обновляем для использования с базой данных
            )
            await callback_query.message.edit_text(
                text=f"Дата начала бронирования: {selected_date.strftime('%d-%m-%Y')}",
                reply_markup=confirm_markup  # Используем результат вызова с await
            )

    elif action == "end":
        if user_id in user_data and "start_date" in user_data[user_id]:
            start_date = user_data[user_id]["start_date"]
            if selected_date < start_date:
                await callback_query.message.answer(
                    "Дата окончания бронирования не может быть раньше даты начала. Пожалуйста, выберите дату окончания снова."
                )
                return

            # Проверяем доступность интервала дат через базу данных
            is_available = await is_date_range_available(
                start_date=start_date,
                end_date=selected_date,
                bike_name=bike['name'])

            if not is_available:
                await callback_query.message.answer(
                    "Этот интервал дат уже забронирован. Пожалуйста, выберите другой интервал."
                )
                # Проверяем, что функция create_calendar_keyboard корректно вызывается с await, если она асинхронная
                calendar_markup = await create_calendar_keyboard(  # Добавлено await для асинхронного вызова
                    year=year,
                    month=month,
                    action="start",
                    model=model,
                    page=page,
                    bike_name=bike['name']
                )
                await callback_query.message.answer(
                    text=f"Сегодняшняя дата: {date.today()} \n\nПожалуйста, выберите дату начала бронирования:",
                    reply_markup=calendar_markup  # Используем результат вызова с await
                )
            else:
                # Проверяем, что функция confirm_end_date корректно вызывается с await, если она асинхронная
                end_confirm_markup = confirm_end_date(  # Добавлено await для асинхронного вызова
                    year=selected_date.year,
                    month=selected_date.month,
                    action="end",
                    model=model,
                    page=page,
                    day=day,
                    booked_dates={}  # Обновляем для использования с базой данных
                )
                await callback_query.message.edit_text(
                    text=f"Дата окончания бронирования: {selected_date.strftime('%d-%m-%Y')}",
                    reply_markup=end_confirm_markup  # Используем результат вызова с await
                )
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

    # Добавляем await, если get_bike является асинхронной функцией
    bike = await get_bike(model, page)  # Добавьте await перед get_bike, если она асинхронная

    current_date = datetime(int(year), int(month), day=1)
    prev_date = current_date - timedelta(days=1)

    # Используем await, если create_calendar_keyboard асинхронная функция
    calendar_markup = await create_calendar_keyboard(  # Уберите await, если функция синхронная
        year=prev_date.year,
        month=prev_date.month,
        action=action,
        model=model,
        page=int(page),
        bike_name=bike['name']
    )

    await callback_query.message.edit_reply_markup(
        reply_markup=calendar_markup
    )


# Обработчик пролистывания календаря вперед
@dp.callback_query(NexMonthCallBack.filter())
async def next_month(callback_query: types.CallbackQuery, callback_data: NexMonthCallBack):
    year = callback_data.year
    month = callback_data.month
    action = callback_data.action
    page = callback_data.page
    model = callback_data.model

    # Используем await, если get_bike асинхронная функция
    bike = await get_bike(model, page)  # Добавьте await, если get_bike является асинхронной функцией

    current_date = datetime(int(year), int(month), day=1)
    next_date = current_date + timedelta(days=31)
    next_date = next_date.replace(day=1)

    # Используем await, если create_calendar_keyboard асинхронная функция
    calendar_markup = await create_calendar_keyboard(  # Уберите await, если функция синхронная
        year=next_date.year,
        month=next_date.month,
        action=action,
        model=model,
        page=int(page),
        bike_name=bike['name']
    )

    await callback_query.message.edit_reply_markup(
        reply_markup=calendar_markup
    )


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

    # Если get_bike является асинхронной, используйте await
    bike = await get_bike(model, page)  # Добавьте await, если get_bike асинхронная

    user_id = callback_query.from_user.id

    if user_id in bike["booked_dates"]:
        del bike["booked_dates"][user_id]  # Сброс забронированных дат для данного пользователя

    # Используйте await, если create_calendar_keyboard асинхронная
    calendar_markup = await create_calendar_keyboard(  # Уберите await, если функция синхронная
        datetime.now().year,
        datetime.now().month,
        "start",
        model,
        page,
        bike["booked_dates"]
    )

    await callback_query.message.edit_text(
        text="Выберите новые даты: ",
        reply_markup=calendar_markup  # Используйте результат вызова create_calendar_keyboard
    )


# Обработчик кнопки "Подтвердить" даты начала бронирования
@dp.callback_query(ConfirmCallBack.filter())
async def confirm_start(callback_query: types.CallbackQuery, callback_data: ConfirmCallBack):
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day
    page = callback_data.page
    model = callback_data.model

    # Используем await, если get_bike асинхронная функция
    bike = await get_bike(model, page)  # Добавьте await, если get_bike асинхронная

    selected_date = date(year, month, day)

    # Используем await, если create_calendar_keyboard асинхронная функция
    calendar_markup = await create_calendar_keyboard(  # Уберите await, если функция синхронная
        year=selected_date.year,
        month=selected_date.month,
        action="end",
        model=model,
        page=page,
        bike_name=bike['name']
    )

    await callback_query.message.edit_text(
        text=f"Дата начала бронирования: {selected_date.strftime('%d-%m-%Y')}\n\nТеперь выберите дату окончания бронирования:",
        reply_markup=calendar_markup  # Используем результат вызова create_calendar_keyboard
    )


# Обработчик кнопки "Подтвердить" даты окончания бронирования
@dp.callback_query(ConfirmEndCallBack.filter())
async def confirm_end(callback_query: types.CallbackQuery, callback_data: ConfirmEndCallBack):
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day
    action = callback_data.action
    page = callback_data.page
    model = callback_data.model
    # bike = get_bike(model, page)
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

    # Используем await, если get_bike асинхронная функция
    bike = await get_bike(model, page)  # Добавляем await, если get_bike асинхронная функция

    user_id = callback_query.from_user.id
    start_date = user_data[callback_query.from_user.id]["start_date"]
    selected_date = date(year, month, day)
    booked_dates = bike["booked_dates"]
    user_data[user_id]["end_date"] = selected_date
    bike_name = bike['name']
    user_data[user_id]['bike_name'] = bike_name
    username = callback_query.from_user.username

    if user_id in user_data and "start_date" in user_data[user_id] and "end_date" in user_data[user_id]:
        if user_id not in booked_dates:
            booked_dates[user_id] = []
        booke = (start_date.strftime('%d-%m-%Y'), selected_date.strftime('%d-%m-%Y'))
        booked_dates[user_id].append(booke)
        start_date = user_data[user_id]["start_date"]
        end_date = user_data[user_id]["end_date"]

        # Получение ссылки на профиль пользователя
        user_profile_link = f"https://t.me/{username}" if username else "Не задано"

        # Отправка сообщения администраторам
        booking_info = (
            f"Пользователь {callback_query.from_user.full_name} ({user_profile_link}) \n\n"
            f"забронировал {user_data[user_id]['bike_name']} \nс {start_date.strftime('%d-%m-%Y')} по {end_date.strftime('%d-%m-%Y')}."
        )

        # Сохраняем данные о бронировании с использованием await
        save_booking_data(user_id, bike['name'], start_date, end_date, username)  # Добавляем await

        # Отправка сообщения админу
        await bot.send_message(ADMIN_GROUP_ID, booking_info)

        await callback_query.message.edit_text(
            text="Ваше бронирование подтверждено!\n\nС вами свяжутся Админы в ближайшее время!",
            reply_markup=booking_information(model, page)
        )
    else:
        await callback_query.message.answer("Произошла ошибка при бронировании. Попробуйте снова.")


# Обработчик кнопки "📋 Мои бронирования"
@dp.callback_query(F.data == "📋 Мои бронирования")
async def my_bookings(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    conn = None
    try:
        # Соединение с базой данных
        conn = await asyncpg.connect(DATABASE_URL)

        # Запрос для получения бронирований пользователя по user_id
        query = """
            SELECT bike_name, start_date, end_date 
            FROM bookings
            WHERE user_id = $1;
            """
        records = await conn.fetch(query, user_id)

        if records:
            booking_info = "Ваши бронирования:\n"
            for i, record in enumerate(records):
                bike_name = record['bike_name']
                start_date = record['start_date'].strftime('%d-%m-%Y')
                end_date = record['end_date'].strftime('%d-%m-%Y')
                booking_info += f"{i + 1}. {bike_name} с {start_date} по {end_date}\n"
        else:
            booking_info = "У вас нет текущих бронирований."

    except asyncpg.PostgresError as e:
        booking_info = f"Ошибка при работе с базой данных: {e}"
    finally:
        if conn:
            await conn.close()  # Закрытие соединения, если оно было установлено

    await callback_query.message.answer(text=booking_info, reply_markup=glavnaya_keyboard())


# Обработчик кнопки "Условия аренды"
@dp.callback_query(F.data == "условия")
async def rent_terms(callback_query: types.CallbackQuery):
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
