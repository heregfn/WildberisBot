admin = ""  # Указать группу в тг для получения сообщений
admin1 = ""  # Указать id Администратора
admin_name = ""  # Указать имя администратора
QIWI_PRIV_KEY = ""  # Указать api key https://qiwi.com/p2p-admin/api
token = ""  # Указать токен полученный от https://t.me/BotFather

import time

import aiogram.dispatcher.middlewares

try:
    import asyncio
    import json
    import random
    import aiohttp
    import aiofiles
    from aiogram import Bot, Dispatcher, executor, types
    from aiogram.dispatcher import FSMContext
    import datetime
    import aioschedule
    import aiosqlite
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton
    from aiogram.dispatcher.filters.state import State, StatesGroup
    from aiogram.contrib.fsm_storage.memory import MemoryStorage
    from aiogram.contrib.middlewares.logging import LoggingMiddleware
    from aiogram.utils.markdown import escape_md
    from aiogram.dispatcher.filters import Text
    from pyqiwip2p import AioQiwiP2P
    from aiogram.utils.exceptions import Throttled
except ImportError as e:
    import os

    os.system('pip3 install asyncio aiohttp aiogram aioschedule aiosqlite pyqiwip2p')
    import asyncio
    import datetime
    import json
    import random
    import aiohttp
    import aiofiles
    from aiogram import Bot, Dispatcher, executor, types
    from aiogram.dispatcher import FSMContext
    import aioschedule
    import aiosqlite
    from pyqiwip2p import AioQiwiP2P
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardMarkup, KeyboardButton
    from aiogram.dispatcher.filters.state import State, StatesGroup
    from aiogram.contrib.fsm_storage.memory import MemoryStorage
    from aiogram.utils.markdown import escape_md
    from aiogram.contrib.middlewares.logging import LoggingMiddleware
    from aiogram.dispatcher.filters import Text
    from aiogram.utils.exceptions import Throttled

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

p2p = AioQiwiP2P(auth_key=QIWI_PRIV_KEY)


class states(StatesGroup):
    set_api = State()
    pay = State()
    edit_sale = State()
    sale_accept = State()
    setup_get = State()
    setup_accept = State()


# ------------------------------QIWI------------------------------
async def get_money(user_id):
    db = await aiosqlite.connect("BalanceUser.db")
    cursor = await db.cursor()
    try:
        await cursor.execute('SELECT user_id, balance FROM user_balance WHERE user_id = ?', (user_id,))
        id_teachers = await cursor.fetchone()
        money = id_teachers[1]
        await cursor.close()
        await db.close()
        return int(money)
    except Exception as e:
        await cursor.execute('INSERT INTO user_balance (user_id, balance) VALUES (?, ?)', (user_id, '0'))
        await db.commit()
        print(e, "get_money")
        return int(0)


async def set_money(user_id, money):
    try:
        user_id = int(user_id)
        money = int(money)
        db = await aiosqlite.connect(r"BalanceUser.db")
        cursor = await db.cursor()
        await cursor.execute(
            'INSERT INTO user_balance (user_id, balance) VALUES (?, ?)',
            (user_id, int(money)))
        await db.commit()
        return True
    except Exception as e:
        print(e, "set_money")
        return False


@dp.message_handler(Text(equals="Баланс"), state="*")
@dp.message_handler(Text(equals="/balance"), state="*")
async def balance(message: types.Message):
    topup = InlineKeyboardButton("Своя сумма", callback_data="topup")
    up99 = InlineKeyboardButton("+99₽", callback_data="up99")
    deposits1 = InlineKeyboardButton("Пополнения", callback_data="deposits")
    writeoffs = InlineKeyboardButton("Списания", callback_data="write-offs")
    back1 = InlineKeyboardButton("Назад", callback_data="back")
    pay = InlineKeyboardMarkup(row_width=2).add(up99, topup, deposits1, writeoffs, back1)
    user_id = message.from_user.id
    text = message.text
    try:
        async with aiosqlite.connect(r"BalanceUser.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT user_id, balance FROM user_balance WHERE user_id = ?', (user_id,))
                user_info = await cursor.fetchone()
                if user_info is None:
                    balance1 = 0
                    await cursor.execute('INSERT INTO user_balance (user_id, balance) VALUES (?, ?)',
                                         (user_id, balance1))
                    await db.commit()
                    await message.answer(
                        f"💰 *Баланс: {balance1}₽*\ \n\n· Тариф: *99₽ / месяц*\ \n\n🔒 Пополнение баланса производится только по Вашему согласию\.\n\n🛡 Деньги с ваших карт в автоматическом режиме *не списываются\.*\ ",
                        reply_markup=pay, parse_mode=types.ParseMode.MARKDOWN_V2)
                else:
                    balance1 = user_info[1]
                    await message.answer(
                        f"💰 *Баланс: {balance1}₽*\ \n\n· Тариф: *99₽ / месяц*\ \n\n🔒 Пополнение баланса производится только по Вашему согласию\. \n\n🛡 Деньги с ваших карт в автоматическом режиме *не списываются\.*\ ",
                        reply_markup=pay, parse_mode=types.ParseMode.MARKDOWN_V2)
    except Exception as e:
        print(e, "balance")
    await DB_user(user_id, text)


@dp.callback_query_handler(Text(startswith="back1"), state="*")
@dp.callback_query_handler(Text(startswith="balance"), state="*")
async def balance(msg: types.CallbackQuery, state: FSMContext):
    await state.finish()
    topup = InlineKeyboardButton("Своя сумма", callback_data="topup")
    up99 = InlineKeyboardButton("+99₽", callback_data="up99")
    deposits = InlineKeyboardButton("Пополнения", callback_data="deposits")
    writeoffs = InlineKeyboardButton("Списания", callback_data="write-offs")
    back = InlineKeyboardButton("Назад", callback_data="back")
    pay = InlineKeyboardMarkup(row_width=2).add(up99, topup, deposits, writeoffs, back)
    user_id = msg.from_user.id
    text = '/balance'
    try:
        async with aiosqlite.connect(r"BalanceUser.db") as db:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT user_id, balance FROM user_balance WHERE user_id = ?', (user_id,))
                user_info = await cursor.fetchone()
                if user_info is None:
                    balance = 0
                    await cursor.execute('INSERT INTO user_balance (user_id, balance) VALUES (?, ?)',
                                         (user_id, balance))
                    await db.commit()
                    await cursor.execute('INSERT INTO user_info (user_id, deposits, offs) VALUES (?, ?, ?)',
                                         (user_id, '', ''))
                    await db.commit()
                    await msg.message.edit_text(
                        f"💰 *Баланс: {balance}₽*\ \n\n· Тариф: *99₽ / месяц*\ \n\n🔒 Пополнение баланса производится только по Вашему согласию\. \n\n🛡 Деньги с ваших карт в автоматическом режиме *не списываются\.*\ ",
                        reply_markup=pay, parse_mode=types.ParseMode.MARKDOWN_V2)
                else:
                    balance = user_info[1]
                    await msg.message.edit_text(
                        f"💰 *Баланс: {balance}₽*\ \n\n· Тариф: *99₽ / месяц*\ \n\n🔒 Пополнение баланса производится только по Вашему согласию\. \n\n🛡 Деньги с ваших карт в автоматическом режиме *не списываются\.*\ ",
                        reply_markup=pay, parse_mode=types.ParseMode.MARKDOWN_V2)

        await msg.answer("")
    except Exception as e:
        print(e, "balance")
    await DB_user(user_id, text)


@dp.callback_query_handler(Text(startswith="Check_"), state="*")
async def Check(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    text = msg.data
    text = text.split("_")[1]
    bill = await p2p.check(bill_id=text)
    bill_id = bill.bill_id
    await msg.answer()
    if bill.status == "PAID":
        db = await aiosqlite.connect("BalanceUser.db")
        cursor = await db.cursor()
        try:
            money = await get_money(user_id)
            async with aiosqlite.connect(r"BalanceUser.db") as db:
                async with db.cursor() as cursor:
                    await cursor.execute('SELECT * FROM user_bill WHERE bill_id = ?', (bill_id,))
                    user_info = await cursor.fetchone()
                    if user_info[0] == user_id:
                        if user_info[3] == 0:
                            money1 = user_info[2]
                            money2 = money + int(user_info[2])
                            await set_money(user_id, money2)
                            use = 1
                            await cursor.execute(
                                'INSERT INTO user_bill (user_id, bill_id, money, use) VALUES (?, ?, ?, ?)',
                                (user_id, bill_id, money1, use))
                            await db.commit()
                            await msg.message.answer(f"💰 Ваш баланс успешно пополнен на {money1}₽")
                            await cursor.execute('SELECT * FROM user_info WHERE user_id = ?', (user_id,))
                            info = await cursor.fetchone()
                            deposits = info[1]
                            deposits = deposits.split()
                            nows = datetime.datetime.now().strftime("%H:%M %d-%m-%Y")
                            deposits.append(f"{nows} - {money1}₽ \n")
                            await cursor.execute(
                                'INSERT INTO user_info (user_id, deposits, offs, sub, sub_date) VALUES (?, ?, ?, ?, ?)',
                                (user_id, ",".join(deposits), info[2], info[3], info[4]))
                            await db.commit()
                            await bot.send_message(admin, text=f'Оплата {user_id} на {money1}р. Всего {money2}')
                        else:
                            await msg.message.edit_text(f"{msg.message.text}\nСчет успешно использован.",
                                                        reply_markup=None)
                            await msg.message.answer(f"Этот счет уже использован.")
                    else:
                        await msg.message.answer("Ты как сюда попал? 0_o")
                        await bot.send_message(admin, text=f'Оплата не по тому user_id {user_id} {user_info[0]}')
        except Exception as e:
            await bot.send_message(admin, text=f'При оплате ошибка {e} у {user_id}')
            await msg.message.answer("Произошла ошибка, передал её администратору, ожидай...")
    else:
        bill_id = InlineKeyboardButton("Проверить оплату", callback_data=f"Check_{bill.bill_id}")
        url = InlineKeyboardButton("Оплатить", url=bill.pay_url)
        cansel = InlineKeyboardButton("Отмена", callback_data=f"Checkoof_{bill.bill_id}")
        topup = InlineKeyboardMarkup(row_width=2).add(url, bill_id).add(cansel)
        await msg.message.edit_text(f"Cчет не оплачен, оплатите счет.", reply_markup=topup)


@dp.callback_query_handler(Text(startswith="Checkoof_"), state="*")
async def Checkoff(msg: types.CallbackQuery):
    await msg.answer()
    user_id = msg.from_user.id
    text = msg.data
    text = text.split("_")[1]
    bill = await p2p.check(bill_id=text)
    bill_id = bill.bill_id
    async with aiosqlite.connect("BalanceUser.db") as db:
        async with db.cursor() as cursor:
            if bill.status == "PAID":
                await msg.message.answer(
                    'Счет был оплачен, пожалуйста активируй его, если ты его ранее не использовал нажми "Проверка оплаты"')
            else:
                await cursor.execute('SELECT * FROM user_bill WHERE bill_id = ?', (bill_id,))
                Id_user = await cursor.fetchone()
                if Id_user != None:
                    await cursor.execute('DELETE FROM user_bill WHERE bill_id = ?', (bill.bill_id,))
                    await db.commit()
                    await p2p.reject(bill_id=bill_id)
                    await bot.send_message(admin,
                                           text=f'Счет был отменен клиентом {user_id}\nКомент {bill.comment}\nBill_id {bill.bill_id}')
                    await msg.message.delete()
                    back = InlineKeyboardButton("Назад", callback_data="back")
                    pay = InlineKeyboardMarkup(row_width=2).add(back)
                    await msg.message.answer("Пополнение баланса отменено.", reply_markup=pay)
                else:
                    await msg.message.delete()
                    pass


@dp.callback_query_handler(Text(startswith="topup"), state="*")
async def Checkoff(msg: types.CallbackQuery):
    await msg.answer("")
    await msg.message.delete()
    back = InlineKeyboardButton("Назад", callback_data="back1")
    pay = InlineKeyboardMarkup(row_width=2).add(back)
    await msg.message.answer("Введите сумму для пополнения баланса:", reply_markup=pay)
    await states.pay.set()


@dp.message_handler(state=states.pay)
async def topups1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    try:
        amount = int(text)
        pass
    except:
        await message.answer(
            "Введенно некорректное значение для пополнения баланса. \nМинимальная сумма пополнения - 10₽.")
        return
    if int(text) <= 1:
        await message.answer("Введи сумму от 10р для пополнения баланса")
    else:
        comment = f'{user_id}_{random.randrange(10000000, 9999999999)}'
        bill = await p2p.bill(amount=amount, lifetime=15, comment=comment)
        bill_id = InlineKeyboardButton("💲 Проверить оплату", callback_data=f"Check_{bill.bill_id}")
        url = InlineKeyboardButton("💳 Перейти к оплате", url=bill.pay_url)
        cansel = InlineKeyboardButton("Отмена", callback_data=f"Checkoof_{bill.bill_id}")
        topup = InlineKeyboardMarkup(row_width=2).add(url, bill_id).add(cansel)
        await message.answer(
            f'💰 Сумма к оплате: *{amount}₽*\ \n\n🔒 Оплата полностью безопасна и производится на стороне платёжной системы\.\n\n🇷🇺 Оплатить можно картой любого российского банка \(Сбер, Тинькофф, Киви и т\.д\.\)\.\n\n🕔 Средства на баланс бота поступают в течение 1\-2 мин\.\n\n🤖 Чтобы активировать бота оплатите и нажмите «Проверить оплату»',
            reply_markup=topup, parse_mode=types.ParseMode.MARKDOWN_V2)
        await bot.send_message(admin,
                               text=f'Тут чел {user_id} хочет оплатить счет на {amount}р, вот ссылка на оплату {bill.pay_url}, Комент {comment}\nBill_id {bill.bill_id}')
        async with aiosqlite.connect(r"BalanceUser.db") as db:
            async with db.cursor() as cursor:
                use = 0
                billamount = bill.amount
                billamount = str(billamount).split('.')[0]
                await cursor.execute('INSERT INTO user_bill (user_id, bill_id, money, use) VALUES (?, ?, ?, ?)',
                                     (user_id, bill.bill_id, billamount, use))
                await db.commit()
                await state.finish()
                await asyncio.sleep(900)
                status = bill.status
                if status == "PAID":
                    try:
                        await bot.send_message(admin,
                                               text=f'Счет был оплачен\nКомент {comment}\nBill_id {bill.bill_id}')
                    except Exception as e:
                        print(e, "topup")
                else:
                    try:
                        await cursor.execute('DELETE FROM user_bill WHERE bill_id = ?', (bill.bill_id,))
                        await db.commit()
                        await bot.send_message(admin,
                                               text=f'Счет был не оплачен\nКомент {comment}\nBill_id {bill.bill_id}')
                    except Exception as e:
                        print(e, "topup1")


@dp.callback_query_handler(Text(startswith="up99"), state="*")
async def topups2(msg: types.CallbackQuery, state: FSMContext):
    await msg.message.delete()
    user_id = msg.from_user.id
    amount = 99
    comment = f'{user_id}_{random.randrange(10000000, 9999999999)}'
    bill = await p2p.bill(amount=amount, lifetime=15, comment=comment)
    bill_id = InlineKeyboardButton("💲 Проверить оплату", callback_data=f"Check_{bill.bill_id}")
    url = InlineKeyboardButton("💳 Перейти к оплате", url=bill.pay_url)
    cansel = InlineKeyboardButton("Отмена", callback_data=f"Checkoof_{bill.bill_id}")
    topup = InlineKeyboardMarkup(row_width=2).add(url, bill_id).add(cansel)
    await msg.message.answer(
        f'💰 Сумма к оплате: *{amount}₽*\ \n\n🔒 Оплата полностью безопасна и производится на стороне платёжной системы\.\n\n🇷🇺 Оплатить можно картой любого российского банка \(Сбер, Тинькофф, Киви и т\.д\.\)\.\n\n🕔 Средства на баланс бота поступают в течение 1\-2 мин\.\n\n🤖 Чтобы активировать бота оплатите и нажмите «Проверить оплату»',
        reply_markup=topup, parse_mode=types.ParseMode.MARKDOWN_V2)
    await bot.send_message(admin,
                           text=f'Тут чел {user_id} хочет оплатить счет на {amount}р, вот ссылка на оплату {bill.pay_url}, Комент {comment}\nBill_id {bill.bill_id}')
    async with aiosqlite.connect("BalanceUser.db") as db:
        async with db.cursor() as cursor:
            use = 0
            billamount = bill.amount
            billamount = str(billamount).split('.')[0]
            await cursor.execute('INSERT INTO user_bill (user_id, bill_id, money, use) VALUES (?, ?, ?, ?)',
                                 (user_id, bill.bill_id, billamount, use))
            await db.commit()
            await state.finish()
            await asyncio.sleep(900)
            status = bill.status
            if status == "PAID":
                try:
                    await bot.send_message(admin, text=f'Счет был оплачен\nКомент {comment}\nBill_id {bill.bill_id}')
                except Exception as e:
                    print(e, "topup")
            else:
                try:
                    await cursor.execute('DELETE FROM user_bill WHERE bill_id = ?', (bill.bill_id,))
                    await db.commit()
                    await bot.send_message(admin, text=f'Счет был не оплачен\nКомент {comment}\nBill_id {bill.bill_id}')
                except Exception as e:
                    print(e, "topup1")
    await msg.answer("")


@dp.callback_query_handler(Text(startswith="back"), state="*")
async def back(msg: types.CallbackQuery, state: FSMContext):
    try:
        button_api = InlineKeyboardButton(text='➕ Добавить API', callback_data='api_add')
        button_balance = InlineKeyboardButton(text='💰 Баланс', callback_data='balance')
        button_support = InlineKeyboardButton(text='👨🏻\u200d💻 Поддержка', url="https://t.me/roboticselleradmin")
        LK = InlineKeyboardMarkup(row_width=2).add(button_api, button_balance, button_support)
        await msg.message.edit_text("Личный кабинет", reply_markup=LK)
        user_id = msg.from_user.id
        last_message = "Назад"
        await DB_user(user_id, last_message)
        await state.finish()
        await msg.answer("")
    except:
        button_api = InlineKeyboardButton(text='➕ Добавить API', callback_data='api_add')
        button_balance = InlineKeyboardButton(text='💰 Баланс', callback_data='balance')
        button_support = InlineKeyboardButton(text='👨🏻\u200d💻 Поддержка', url="https://t.me/roboticselleradmin")
        LK = InlineKeyboardMarkup(row_width=2).add(button_api, button_balance, button_support)
        await msg.message.delete()
        await msg.message.answer("Личный кабинет", reply_markup=LK)
        user_id = msg.from_user.id
        last_message = "Назад"
        await DB_user(user_id, last_message)
        await state.finish()
        await msg.answer("")


@dp.callback_query_handler(Text(startswith="deposits"))
async def deposits(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    await msg.answer("")
    async with aiosqlite.connect(r"BalanceUser.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM user_info WHERE user_id = ?', (user_id,))
            user_info = await cursor.fetchone()
            if user_info is None:
                await cursor.execute('INSERT INTO user_info (user_id, deposits, offs) VALUES (?, ?, ?)',
                                     (user_id, '', ''))
                await db.commit()
                await msg.message.answer("🧾 Пополнения\n\nПополнений ещё не было.")
            else:
                if user_info[1] != "":
                    dates = user_info[1].split(',')
                    await msg.message.answer(f"🧾 Пополнения\n\n{''.join(dates)}")
                else:
                    await msg.message.answer("🧾 Пополнения\n\nПополнений ещё не было.")


@dp.callback_query_handler(Text(startswith="write-offs"))
async def offs(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    await msg.answer("")
    async with aiosqlite.connect(r"BalanceUser.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute('SELECT * FROM user_info WHERE user_id = ?', (user_id,))
            user_info = await cursor.fetchone()
            if user_info is None:
                await cursor.execute('INSERT INTO user_info (user_id, deposits, offs) VALUES (?, ?, ?)',
                                     (user_id, '', ''))
                await db.commit()
                await msg.message.answer("🧾 Списания\n\nСписаний с вашего баланса ещё не было.")
            else:
                if user_info[2] != "":
                    dates = user_info[2].split(',')
                    await msg.message.answer(f"🧾 Списания\n\n{''.join(dates)}")
                else:
                    await msg.message.answer("🧾 Списания\n\nСписаний с вашего баланса ещё не было.")


# ____________________________________________________________


async def set_default_commands():
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Главное меню"),
        types.BotCommand("balance", "Баланс"),
        types.BotCommand("articles", "Автоматический редактор скидки"),
        types.BotCommand("prices", "Управление ценами")
    ])


async def MassSend(text, notf):
    db = await aiosqlite.connect(r"Users.db")
    cursor = await db.cursor()
    await cursor.execute('SELECT user_id FROM user')
    user_ids = await cursor.fetchall()
    loop = 0
    loop1 = 1
    d = len(user_ids)
    for user_id in user_ids:
        try:
            await bot.send_message(user_id[0], disable_notification=notf, text=text)
            await bot.send_message(admin, disable_notification=True,
                                   text=f'[{loop}/{d}]({user_id[0]})')
            loop = loop + 1
            await asyncio.sleep(0.4)
            if loop == 80:
                await asyncio.sleep(20)
        except Exception as e:
            await bot.send_message(admin, disable_notification=False, text=f'{user_id[0]} ERROR: {e}')
            loop1 = loop1 + 1
    await bot.send_message(admin, disable_notification=False, text=f'ERRORS: {loop1}')
    await cursor.close()
    await db.close()


async def MassSendSubs(text, notf):
    db = await aiosqlite.connect(r"Users.db")
    cursor = await db.cursor()
    await cursor.execute('SELECT * FROM user')
    user_ids = await cursor.fetchall()
    loop = 0
    loop1 = 1
    d = len(user_ids)
    for user_id in user_ids:
        deposits = user_id[1]
        offs = user_id[2]
        sub = user_id[3]
        sub_date = user_id[4]
        if str(sub) == str(1):
            try:
                await bot.send_message(user_id[0], disable_notification=notf, text=text)
                await bot.send_message(admin, disable_notification=True,
                                       text=f'[{loop}/{d}]({user_id[0]})')
                loop = loop + 1
                await asyncio.sleep(0.4)
                if loop == 80:
                    await asyncio.sleep(20)
            except Exception as e:
                await bot.send_message(admin, disable_notification=False, text=f'{user_id[0]} ERROR: {e}')
                loop1 = loop1 + 1
    await bot.send_message(admin, disable_notification=False, text=f'ERRORS: {loop1}')
    await cursor.close()
    await db.close()


async def DB_Get_Passed(user_id):
    async with aiosqlite.connect(r"BalanceUser.db") as db:
        cursor = await db.cursor()
        a = await dp.bot.get_chat(user_id)
        await cursor.execute('SELECT * FROM user_info WHERE user_id = ?', (user_id,))
        info = await cursor.fetchone()
        if info is not None:
            passed = info[3]
            if passed != 0:
                return True
            else:
                return False
        else:
            await cursor.execute('INSERT INTO user_info (user_id, deposits, offs) VALUES (?, ?, ?)',
                                 (user_id, '', ''))
            await db.commit()
            return False


async def DB_key(user_id, key):
    try:
        async with aiosqlite.connect(r"Users.db") as db:
            cursor = await db.cursor()
            a = await dp.bot.get_chat(user_id)
            await cursor.execute('SELECT * FROM user WHERE user_id = ?', (user_id,))
            group = await cursor.fetchone()
            if group is not None:
                user_id = group[0]
                nmid = key
                key = group[2]
                key1 = group[3]
                last_message = group[4]
                balanse = group[5]
                nm = group[6]
                await cursor.execute(
                    'INSERT INTO user (user_id, nmid, key, key1, last_message, balanse, nm) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (user_id, nmid, key, key1, last_message, balanse, nm))
                await db.commit()
                await bot.send_message(admin, f"Юзер @{a.username}({a.id}: Ключ был успешно записан в БД!")
                return True
            else:
                await DB_reg(user_id, f"/key {key}")
                return False
    except Exception as x:
        print(f"[ERROR]: DB_key: {x}")


async def DB_nmid(user_id):
    try:
        async with aiosqlite.connect(r"Users.db") as db:
            cursor = await db.cursor()
            await dp.bot.get_chat(user_id)
            await cursor.execute('SELECT * FROM user WHERE user_id = ?', (user_id,))
            group = await cursor.fetchone()
            if group is not None:
                key = group[2]
                key1 = group[3]
                nm = group[6]
                if key == "[]":
                    key = None
                if key1 == "[]":
                    key1 = None
                return key, key1, nm
            else:
                await DB_reg(user_id, f"DB_nmid")
                return False
    except Exception as q:
        print(f"[ERROR]: DB_nmid: {q}")


async def DB_nmid_set_key(user_id, key, key1, nm):
    try:
        async with aiosqlite.connect(r"Users.db") as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT * FROM user WHERE user_id = ?', (user_id,))
            group = await cursor.fetchone()
            if group is not None:
                user_id = group[0]
                nmid = group[1]
                if key is None:
                    key = group[2]
                if key1 is None:
                    key1 = group[3]
                if nm is None:
                    nm = group[6]
                last_message = group[4]
                balanse = group[5]
                await cursor.execute(
                    'INSERT INTO user (user_id, nmid, key, key1, last_message, balanse, nm) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (user_id, nmid, str(key), str(key1), last_message, balanse, str(nm)))
                await db.commit()
            else:
                await DB_reg(user_id, f"DB_nmid_set_key")
                return False
    except Exception as e1:
        print(f"[ERROR]: DB_nmid_set_key: {e1}")


async def DB_get_key(user_id):
    try:
        async with aiosqlite.connect(r"Users.db") as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT * FROM user WHERE user_id = ?', (user_id,))
            group = await cursor.fetchone()
            if group is not None:
                return group[1]
            else:
                await DB_reg(user_id, f"")
                return None
    except Exception as ex:
        print(f"[ERROR]: DB_get_key: {ex}")


async def DB_reg(user_id: str, last_message: str):
    try:
        async with aiosqlite.connect(r"Users.db") as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT user_id FROM user WHERE user_id = ?', (user_id,))
            user_idsa = await cursor.fetchone()
            a = await dp.bot.get_chat(user_id)
            if user_idsa is None:
                await cursor.execute('INSERT INTO user (user_id, last_message) VALUES (?, ?)', (user_id, last_message))
                await db.commit()
                a = await dp.bot.get_chat(user_id)
                await bot.send_message(admin, f'Регистрация @{a.username}({user_id}): {last_message}')
            elif user_idsa is not None:
                await DB_user(user_id, f'Повторная Регистрация {last_message}')
    except Exception as ex:
        print(f"[ERROR]: DB_reg: {ex}")


async def DB_user(user_id: str, last_message: str):
    try:
        async with aiosqlite.connect(r"Users.db") as db:
            cursor = await db.cursor()
            a = await dp.bot.get_chat(user_id)
            await cursor.execute('SELECT * FROM user WHERE user_id = ?', (user_id,))
            group = await cursor.fetchone()
            if group is not None:
                user_id = group[0]
                nmid = group[1]
                key = group[2]
                key1 = group[3]
                balanse = group[5]
                nm = group[6]
                await cursor.execute(
                    'INSERT INTO user (user_id, nmid, key, key1, last_message, balanse, nm) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (user_id, nmid, key, key1, last_message, balanse, nm))
                await db.commit()
                await bot.send_message(admin, f"Юзер @{a.username}({a.id}): {last_message}")
            else:
                await DB_reg(user_id, last_message)
    except Exception as e3:
        print(f"[ERROR]: DB_user: {e3}")


@dp.message_handler(commands="start", state="*")
async def start(message: types.Message, state: FSMContext):
    button_api = InlineKeyboardButton(text='➕ Добавить API', callback_data='api_add')
    button_balance = InlineKeyboardButton(text='💰 Баланс', callback_data='balance')
    button_support = InlineKeyboardButton(text='👨🏻\u200d💻 Поддержка', url="https://t.me/roboticselleradmin")
    LK = InlineKeyboardMarkup(row_width=2).add(button_api, button_balance, button_support)
    await message.answer("Личный кабинет", reply_markup=LK)
    user_id = message.from_user.id
    last_message = message.text
    await DB_reg(user_id, last_message)
    await DB_Get_Passed(user_id)
    await state.finish()
    await set_default_commands()


@dp.callback_query_handler(Text(startswith="api_add"))
async def api_add_callback(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        url = "https://seller.wildberries.ru/supplier-settings/access-to-new-api"
        keyboard = InlineKeyboardMarkup()
        button = InlineKeyboardButton('Ссылка', url=url)
        button1 = InlineKeyboardButton('Назад', callback_data="back")
        keyboard.add(button, button1)
        with open(r'key.jpg', 'rb') as doc:
            await msg.message.delete()
            await msg.message.answer_photo(photo=doc,
                                           caption='🛠 ПОДКЛЮЧЕНИЕ API\n\n1️⃣ Зайдите в личный кабинет Wildberries в раздел "Настройки > Доступ к новому API".\n\n2️⃣ Задайте имя и нажмите "Создать ключ".\n\n3️⃣ Скопируйте и отправьте ключ в сообщении этого чата:',
                                           reply_markup=keyboard)
        await states.set_api.set()
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.message_handler(commands="key", state="*")
async def Set_Key(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        key = message.get_args()
        user_id = message.from_user.id
        if key != "":
            await bot.send_message(admin,
                                   f"Юзер @{message.from_user.username}({message.from_user.id}): Запросил проверку своего ключа.")
            msg = await message.answer("Проверка ключа....")
            headers = {
                'Authorization': key,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
            if response[0] == 200:
                answer = await DB_key(user_id, key)
                if answer:
                    await msg.edit_text("Проверка выполнена успешно! Ваш ключ был записан в БД.")
                else:
                    await msg.edit_text(
                        "Проверка выполнена успешно! Ваш ключ не был записан в БД, пожалуйста скопируйте свое сообщение и отправьте мне его еще раз!")
            elif response[0] == 401:
                await msg.edit_text("Api ключ не верен!")
            elif response[0] == 500:
                await msg.edit_text("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
        else:
            url = "https://seller.wildberries.ru/supplier-settings/access-to-new-api"
            keyboard = InlineKeyboardMarkup()
            button = InlineKeyboardButton('Ссылка', url=url)
            keyboard.add(button)
            await message.answer(
                "Вы не указали ключ!\nПолучить ключ можно в личном кабинете, если вы не получали ключ пожалуйста перейдите по ссылке ниже для его создания.\n\nПример: '/key Api_key'",
                reply_markup=keyboard)
    else:
        await message.answer("Приобретите подписку для продолжения использования бота")
        await message.delete()
    await DB_user(user_id, message.text)


@dp.message_handler(commands="articles", state="*")
async def Get_articles(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    next = InlineKeyboardButton(f"Выбрать все", callback_data=f'Sellect_all')
                    inline_kb1 = inline_kb1.add(next)
                    a = await DB_nmid(user_id)
                    if a[2] is not None:
                        a = a[2].split(',')
                    else:
                        a = []
                    for nm in nms:
                        l = len(nms) - 1
                        if l != loop:
                            if loop >= 6:
                                if loop1 == 1:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Next_{nm}')
                                    inline_btn_1 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, next)
                                elif loop1 == 2:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Next_{nm}')
                                    inline_btn_2 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, next)
                                break
                            if str(nm) in a:
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                elif loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                    loop1 = 0
                            else:
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm} ❌", callback_data=f'select_None_{nm}')
                                elif loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm} ❌", callback_data=f'select_None_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                    loop1 = 0
                                    # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                            loop1 = loop1 + 1
                            loop = loop + 1
                        else:
                            if str(nm) in a:
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1)
                                if loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                            else:
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm} ❌", callback_data=f'select_None_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1)
                                if loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm} ❌", callback_data=f'select_None_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                    inline_kb1.add(InlineKeyboardButton(f"🔁 Установить стандартные значения скидок",
                                                        callback_data=f'Set_Standart_Sale'))
                    await message.answer(
                        "Выберите артикулы, на которые автоматически будет установлена скидка -30% от стоимости товара с 01:00 до 06:00 по МСК",
                        reply_markup=inline_kb1)
                    await DB_user(user_id, last_message=message.text)
                elif response[0] == 401:
                    await message.answer("Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
        else:
            button_api = InlineKeyboardButton(text='➕ Добавить API', callback_data='api_add')
            button_balance = InlineKeyboardButton(text='💰 Баланс', callback_data='balance')
            button_support = InlineKeyboardButton(text='👨🏻\u200d💻 Поддержка', url="https://t.me/roboticselleradmin")
            LK = InlineKeyboardMarkup(row_width=2).add(button_api, button_balance, button_support)
            await message.answer("У вас не указан API ключ!", reply_markup=LK)
    else:
        await message.answer("Приобретите подписку для продолжения использования бота")
        await message.delete()
    await DB_user(user_id, message.text)


@dp.message_handler(commands="prices", state="*")
async def Get_articles(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        Edit_menu = InlineKeyboardButton(text="Установка скидки", callback_data=f'Edit_menu')
        Set_price = InlineKeyboardButton(text='Установка цены', callback_data='Setup_menu')
        LK = InlineKeyboardMarkup(row_width=2).add(Edit_menu, Set_price)
        await message.answer("Выберите, что вы хотите поменять", reply_markup=LK)
        await DB_user(user_id, message.text)
    else:
        await message.delete()
        await message.answer("Приобретите подписку для продолжения использования бота")
    await DB_user(message.from_user.id, message.text)


# _____________________Menu_ALL__________________________
@dp.callback_query_handler(Text(startswith="Sellect_all"))
async def Sellect_all(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        user_id = msg.from_user.id
        key = await DB_get_key(user_id)
        await msg.answer('')
        if key is not None:
            headers = {
                'Authorization': key,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
            if response[0] == 200:
                answer = response[1]
                nms = []
                keys = []
                key1 = []
                for info in answer:
                    nm = info.get("nmId")
                    discount = info.get("discount")
                    if int(discount) > 5:
                        discountsale = discount - 29
                        if int(discountsale) < 5:
                            discountsale = 5
                    else:
                        discountsale = 5
                    keys.append({
                        "discount": discountsale,
                        "nm": nm
                    })
                    key1.append({
                        "discount": discount,
                        "nm": nm
                    })
                    nms.append(f"{nm},")
                inline = msg.message.reply_markup.inline_keyboard
                for i in inline:
                    for a in i:
                        text = a.text.split()
                        if text[1] == "✅" or text[1] == "❌":
                            a.text = f"{text[0]} ✅"
                            a.callback_data = f"selecT_{text[0]}"
                        elif text[1] == "все":
                            a.text = f"Удалить все"
                            a.callback_data = "dell_all"
                inline = msg.message.reply_markup
                inline.add(InlineKeyboardButton(f"🔁 Установить стандартные значения скидок",
                                                callback_data=f'Set_Standart_Sale'))
                await msg.message.edit_text(
                    "Выберите артикулы, на которые автоматически будет установлена скидка -30% от стоимости товара с 01:00 до 06:00 по МСК",
                    reply_markup=inline)
                await DB_nmid_set_key(user_id, keys, key1, "".join(nms))
            elif response[0] == 401:
                await msg.message.answer("Api ключ не верен!")
            elif response[0] == 500:
                await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="dell_all"))
async def dell_all(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        user_id = msg.from_user.id
        key = await DB_get_key(user_id)
        await msg.answer('')
        if key is not None:
            headers = {
                'Authorization': key,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
            if response[0] == 200:
                nms = []
                keys = []
                key1 = []
                inline = msg.message.reply_markup.inline_keyboard
                for i in inline:
                    for a in i:
                        text = a.text.split()
                        if text[1] == "✅" or text[1] == "❌":
                            a.text = f"{text[0]} ❌"
                            a.callback_data = f"select_None_{text[0]}"
                        elif text[1] == "все":
                            a.text = f"Выбрать все"
                            a.callback_data = "Sellect_all"
                inline = msg.message.reply_markup
                inline.add(InlineKeyboardButton(f"🔁 Установить стандартные значения скидок",
                                                callback_data=f'Set_Standart_Sale'))
                await msg.message.edit_text(
                    "Выберите артикулы, на которые автоматически будет установлена скидка -30% от стоимости товара с 01:00 до 06:00 по МСК",
                    reply_markup=inline)
                await DB_nmid_set_key(user_id, keys, key1, "".join(nms))
            elif response[0] == 401:
                await msg.message.answer("Api ключ не верен!")
            elif response[0] == 500:
                await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="selecT_"))
async def selecT_callback(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        nm = msg.data.split("selecT_")[1]
        nm_s = nm
        inline = msg.message.reply_markup.inline_keyboard
        await msg.answer("")
        user_id = msg.from_user.id
        key = await DB_get_key(user_id)
        await msg.answer('')
        if key is not None:
            headers = {
                'Authorization': key,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
            if response[0] == 200:
                answer = response[1]
                nms = []
                nmids = []
                keys = []
                key1 = []
                nmids = []
                keyses = await DB_nmid(user_id)
                temp = []
                if keyses[2] is not None:
                    keyses = keyses[2].split(",")
                    for k in keyses:
                        if str(k) == str(nm_s):
                            pass
                        else:
                            temp.append(k)
                    keyses = temp
                else:
                    keyses = []
                for info in answer:
                    nm = info.get("nmId")
                    discount = info.get("discount")
                    if int(discount) > 5:
                        discountsale = discount - 29
                        if int(discountsale) < 5:
                            discountsale = 5
                    else:
                        discountsale = 5
                    if str(nm) in keyses:
                        keys.append({
                            "discount": discountsale,
                            "nm": nm
                        })
                        key1.append({
                            "discount": discount,
                            "nm": nm
                        })
                        nms.append(f"{nm},")
                    nmids.append(nm)
                for i in inline:
                    for a in i:
                        if a.text == f"{nm_s} ✅":
                            a.text = f"{nm_s} ❌"
                            a.callback_data = f"select_None_{nm_s}"
                            print(f"select_None_{nm_s}")
                inline = msg.message.reply_markup
                await msg.message.edit_text(
                    "Выберите артикулы, на которые автоматически будет установлена скидка -30% от стоимости товара с 01:00 до 06:00 по МСК",
                    reply_markup=inline)
                await DB_nmid_set_key(user_id, keys, key1, "".join(nms))
            elif response[0] == 401:
                await msg.message.answer("Api ключ не верен!")
            elif response[0] == 500:
                await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
        await msg.message.delete()
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="select_None_"))
async def select_None_callback(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        nm = msg.data.split("select_None_")[1]
        nm_s = nm
        inline = msg.message.reply_markup.inline_keyboard
        await msg.answer("")
        user_id = msg.from_user.id
        key = await DB_get_key(user_id)
        await msg.answer('')
        if key is not None:
            headers = {
                'Authorization': key,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
            if response[0] == 200:
                answer = response[1]
                nms = []
                nmids = []
                keys = []
                key1 = []
                nmids = []
                keyses = await DB_nmid(user_id)
                if keyses[2] is not None:
                    keyses = keyses[2].split(",")
                    keyses.append(nm)
                else:
                    keyses = []
                    keyses.append(nm)
                for info in answer:
                    nm = info.get("nmId")
                    discount = info.get("discount")
                    if int(discount) > 5:
                        discountsale = discount - 29
                        if int(discountsale) < 5:
                            discountsale = 5
                    else:
                        discountsale = 5
                    if str(nm) in keyses:
                        keys.append({
                            "discount": discountsale,
                            "nm": nm
                        })
                        key1.append({
                            "discount": discount,
                            "nm": nm
                        })
                        nms.append(f"{nm},")
                    nmids.append(nm)
                for i in inline:
                    for a in i:
                        if a.text == f"{nm_s} ❌":
                            a.text = f"{nm_s} ✅"
                            a.callback_data = f"selecT_{nm_s}"
                inline = msg.message.reply_markup
                await msg.message.edit_text(
                    "Выберите артикулы, на которые автоматически будет установлена скидка -30% от стоимости товара с 01:00 до 06:00 по МСК",
                    reply_markup=inline)
                await DB_nmid_set_key(user_id, keys, key1, "".join(nms))
            elif response[0] == 401:
                await msg.message.answer("Api ключ не верен!")
            elif response[0] == 500:
                await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="Last_"))
async def Last_callback(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        nm = msg.data.split("Last_")[1]
        nm_s = nm
        user_id = msg.from_user.id
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    loop23 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    a = await DB_nmid(user_id)
                    if a[2] is not None:
                        a = a[2].split(',')
                    else:
                        a = []
                    passed = 0
                    for nm in nms:
                        if str(nm_s) == str(nm):
                            l = len(nms) - 1 - loop23
                            passed = 1
                        if passed == 1:
                            if l != loop:
                                passed = 1
                                if loop >= 6:
                                    if loop1 == 1:
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Next_{nm}')
                                        inline_btn_1 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1, next)
                                    elif loop1 == 2:
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Next_{nm}')
                                        inline_btn_2 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, next)
                                    break
                                if str(nm) in a:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                    elif loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                        loop1 = 0
                                else:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm} ❌",
                                                                            callback_data=f'select_None_{nm}')
                                    elif loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm} ❌",
                                                                            callback_data=f'select_None_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                        loop1 = 0
                                        # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                                loop1 = loop1 + 1
                                loop = loop + 1
                            else:
                                if str(nm) in a:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1)
                                    if loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                else:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm} ❌",
                                                                            callback_data=f'select_None_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1)
                                    if loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm} ❌",
                                                                            callback_data=f'select_None_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                        loop23 = loop23 + 1
                    inline_kb1.add(InlineKeyboardButton(f"🔁 Установить стандартные значения скидок",
                                                        callback_data=f'Set_Standart_Sale'))
                    await msg.message.edit_text(
                        "Выберите артикулы, на которые автоматически будет установлена скидка -30% от стоимости товара с 01:00 до 06:00 по МСК",
                        reply_markup=inline_kb1)
                    await DB_user(user_id, last_message="Выбор в меню артиклов")
                elif response[0] == 401:
                    await msg.message.answer("Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="Next_"))
async def Next_callback(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        nm = msg.data.split("Next_")[1]
        nm_s = nm
        inl = msg.message.reply_markup.inline_keyboard
        loop = 0
        start_nm = 0
        passed = 0
        for i in inl:
            for a in i:
                text = a.text.split()[1]
                callback_data = a.callback_data
                if text != f"все":
                    passed = 1
                    start_nm = a.text.split()[0]
                    break
            if passed == 1:
                break
        user_id = msg.from_user.id
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    loop23 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    next = InlineKeyboardButton(f"Выбрать все", callback_data=f'Sellect_all')
                    inline_kb1 = inline_kb1.add(next)
                    a = await DB_nmid(user_id)
                    if a[2] is not None:
                        a = a[2].split(',')
                    else:
                        a = []
                    passed = 0
                    for nm in nms:
                        if passed == 1:
                            if l != loop:
                                if loop >= 6:
                                    if nm in a:
                                        if loop1 == 1:
                                            inline_btn_1 = InlineKeyboardButton(f"{nm} ✅",
                                                                                callback_data=f'select_None_{nm}')
                                            next = InlineKeyboardButton(f"➡️", callback_data=f'Next_{nm}')
                                            last = InlineKeyboardButton(f"⬅️", callback_data=f"Last_{start_nm}")
                                            inline_kb1 = inline_kb1.add(inline_btn_1, last, next)
                                        elif loop1 == 2:
                                            inline_btn_2 = InlineKeyboardButton(f"{nm} ✅",
                                                                                callback_data=f'select_None_{nm}')
                                            next = InlineKeyboardButton(f"➡️", callback_data=f'Next_{nm}')
                                            last = InlineKeyboardButton(f"⬅️", callback_data=f"Last_{start_nm}")
                                            inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last, next)
                                    else:
                                        if loop1 == 1:
                                            inline_btn_1 = InlineKeyboardButton(f"{nm} ❌",
                                                                                callback_data=f'select_None_{nm}')
                                            next = InlineKeyboardButton(f"➡️", callback_data=f'Next_{nm}')
                                            last = InlineKeyboardButton(f"⬅️", callback_data=f"Last_{start_nm}")
                                            inline_kb1 = inline_kb1.add(inline_btn_1, last, next)
                                        elif loop1 == 2:
                                            inline_btn_2 = InlineKeyboardButton(f"{nm} ❌",
                                                                                callback_data=f'select_None_{nm}')
                                            next = InlineKeyboardButton(f"➡️", callback_data=f'Next_{nm}')
                                            last = InlineKeyboardButton(f"⬅️", callback_data=f"Last_{start_nm}")
                                            inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last, next)
                                    break
                                if str(nm) in a:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                    elif loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                        loop1 = 0
                                else:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm} ❌",
                                                                            callback_data=f'select_None_{nm}')
                                    elif loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm} ❌",
                                                                            callback_data=f'select_None_{nm}')
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                        loop1 = 0
                                        # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                            else:
                                if str(nm) in a:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(last, inline_btn_1)
                                    if loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm} ✅", callback_data=f'selecT_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last)
                                else:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm} ❌",
                                                                            callback_data=f'select_None_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, last)
                                    if loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm} ❌",
                                                                            callback_data=f'select_None_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last)
                            loop = loop + 1
                            loop1 = loop1 + 1
                        if str(nm) == str(nm_s):
                            passed = 1
                            l = len(nms) - loop23 - 1
                        loop23 = loop23 + 1
                    inline_kb1.add(InlineKeyboardButton(f"🔁 Установить стандартные значения скидок",
                                                        callback_data=f'Set_Standart_Sale'))
                    await msg.message.edit_text(
                        "Выберите артикулы, на которые автоматически будет установлена скидка -30% от стоимости товара с 01:00 до 06:00 по МСК",
                        reply_markup=inline_kb1)
                    await DB_user(user_id, last_message="Выбор в меню артиклов")
                elif response[0] == 401:
                    await msg.message.answer("Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


# ____________________EDIT__________________________________


@dp.callback_query_handler(Text(startswith="Edit_Last_"))
async def Edit_Last_callback(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        nm = msg.data.split("Last_")[1]
        nm_s = nm
        user_id = msg.from_user.id
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    loop23 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    passed = 0
                    start_nm = msg.data.split("Edit_Next_")
                    for nm in nms:
                        if str(nm_s) == str(nm):
                            l = len(nms) - 1 - loop23
                            passed = 1
                        if passed == 1:
                            if l != loop:
                                passed = 1
                                if loop >= 6:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm}",
                                                                            callback_data=f'edit_{nm}')
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Edit_Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, last, next)
                                    elif loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm}",
                                                                            callback_data=f'edit_{nm}')
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Edit_Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last, next)
                                    break
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                elif loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                    loop1 = 0
                                    # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                            else:
                                if loop1 == 1:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, next)
                                elif loop1 == 2:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, next)
                                break
                        loop23 = loop23 + 1
                        loop1 = loop1 + 1
                        loop = loop + 1
                    inline_kb1.add(InlineKeyboardButton(f"Назад",
                                                        callback_data=f'Set_Standart_Sale'))
                    await msg.message.edit_text(
                        "Выберите артикул, на который нужно установить новую скидку",
                        reply_markup=inline_kb1)
                    await DB_user(user_id, last_message="Выбор в меню артиклов")
                elif response[0] == 401:
                    await msg.message.answer("Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="Edit_Next_"))
async def Edit_Next_callback(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        nm = msg.data.split("Edit_Next_")[1]
        nm_s = nm
        inl = msg.message.reply_markup.inline_keyboard
        loop = 0
        start_nm = 0
        passed = 0
        for i in inl:
            for a in i:
                text = a.text.split()[0]
                callback_data = a.callback_data
                if text != f"все":
                    passed = 1
                    start_nm = a.text.split()[0]
                    break
            if passed == 1:
                break
        user_id = msg.from_user.id
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    loop23 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    passed = 0
                    for nm in nms:
                        if passed == 1:
                            if l != loop:
                                if loop >= 6:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm}",
                                                                            callback_data=f'edit_{nm}')
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Edit_Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, last, next)
                                    elif loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm}",
                                                                            callback_data=f'edit_{nm}')
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Edit_Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last, next)
                                    break
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}",
                                                                        callback_data=f'edit_{nm}')
                                elif loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}",
                                                                        callback_data=f'edit_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                    loop1 = 0
                                    # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                            else:
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}",
                                                                        callback_data=f'edit_{nm}')
                                    last = InlineKeyboardButton(f"⬅️", callback_data=f"Edit_Last_{start_nm}")
                                    inline_kb1 = inline_kb1.add(inline_btn_1, last)
                                if loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}",
                                                                        callback_data=f'edit_{nm}')
                                    last = InlineKeyboardButton(f"⬅️", callback_data=f"Edit_Last_{start_nm}")
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last)
                            loop = loop + 1
                            loop1 = loop1 + 1
                        if str(nm) == str(nm_s):
                            passed = 1
                            l = len(nms) - loop23 - 1
                        loop23 = loop23 + 1
                    inline_kb1.add(InlineKeyboardButton(f"Назад",
                                                        callback_data=f'Set_Standart_Sale'))
                    await msg.message.edit_text(
                        "Выберите артикул, на который нужно установить новую скидку",
                        reply_markup=inline_kb1)
                    await DB_user(user_id, last_message="Выбор в меню артиклов")
                elif response[0] == 401:
                    await msg.message.answer("Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="edit_yes"), state="*")
async def edit_yes_callback(msg: types.CallbackQuery, state: FSMContext):
    user_id = msg.from_user.id
    a = await state.get_data()
    await state.finish()
    if a != {}:
        sale = a.get("sale")
        nm = a.get("nm")
        cost = a.get("cost")
        headers = {
            'Authorization': await DB_get_key(user_id),
        }
        async with aiohttp.ClientSession() as session:
            response = await Get_Info(headers, session)
            if response[0] == 200:
                payload = [{
                    "discount": int(sale),
                    "nm": int(nm)
                }]
                responses = await Set_Sale(headers, session, payload)
                if int(responses[0]) == 200:
                    await msg.message.edit_text(
                        f"🟢 Скидка <b>{sale}%</b>(<b>{cost}₽</b>) успешно установлена на артикул <code>{nm}</code>",
                        reply_markup=None, parse_mode="HTML")
                elif int(responses[0]) == 400:
                    backs = InlineKeyboardButton(text='Назад', callback_data=f"edit_{nm}")
                    key = InlineKeyboardMarkup().add(backs)
                    error = responses[1].get("errors")[0].replace(";", '.\n    ')
                    passed = 1
                    temps = []
                    for temp in error.split():
                        if passed == 1:
                            passed = 0
                            temp = "\n" + temp.title()
                        if "." in temp:
                            passed = 1
                        temps.append(temp)
                    await msg.message.edit_text(f"🔴 WB вернул ошибку:\n    {' '.join(temps)}", reply_markup=key)
            elif response[0] == 401:
                await msg.message.edit_text("Api ключ не верен!")
            elif response[0] == 500:
                await msg.message.edit_text("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.edit_text("Произошла ошибка, попробуйте снова.")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="edit_not"), state="*")
async def edit_callback(msg: types.CallbackQuery, state: FSMContext):
    user_id = msg.from_user.id
    await msg.message.edit_text("Хорошо отменено :)")
    await state.finish()
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="edit_"), state="*")
async def edit_callback(msg: types.CallbackQuery, state: FSMContext):
    user_id = msg.from_user.id
    nm = msg.data.split("edit_")[1]
    answer = await DB_get_key(user_id)
    await state.finish()
    if answer is not None:
        headers = {
            'Authorization': answer,
        }
        async with aiohttp.ClientSession() as session:
            response = await Get_Info(headers, session)
            if response[0] == 200:
                for info in response[1]:
                    if int(info.get("nmId")) == int(nm):
                        nm_sale = info.get("price")
                        sale = info.get("discount")
                        cost = nm_sale - (float(sale) / 100 * nm_sale)
                        backs = InlineKeyboardButton(text='Назад', callback_data="Edit_menu")
                        key = InlineKeyboardMarkup().add(backs)
                        await msg.message.edit_text(
                            f'<i>Артикул</i> <code>{nm}</code>\nТекущая скидка – <b>{info.get("discount")}%\n</b>Текущая цена после скидки – <b>{int(cost)}₽\n\n</b>Бот может автоматически поставить нужный процент скидки при отправки конечной стоимости. \n\nВведите конечную стоимость или размер скидки <b>со знаком %</b>:',
                            reply_markup=key, parse_mode="HTML")
                        await states.edit_sale.set()
                        await state.update_data(nm=nm, message_id=msg.message.message_id, chat_id=msg.message.chat.id)
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="Edit_menu"), state="*")
async def Get_articles(msg: types.CallbackQuery, state: FSMContext):
    user_id = msg.from_user.id
    await state.finish()
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    for nm in nms:
                        l = len(nms) - 1
                        if l != loop:
                            if loop >= 6:
                                if loop1 == 1:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, next)
                                elif loop1 == 2:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, next)
                                break
                            if loop1 == 1:
                                inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                            elif loop1 == 2:
                                inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                loop1 = 0
                                # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                            loop1 = loop1 + 1
                            loop = loop + 1
                        else:
                            if loop1 == 1:
                                inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                inline_kb1 = inline_kb1.add(inline_btn_1)
                            if loop1 == 2:
                                inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                    inline_kb1.add(InlineKeyboardButton(f"Назад",
                                                        callback_data=f'Set_Standart_Sale'))
                    await msg.message.edit_text(
                        "Выберите артикул, на который нужно установить новую скидку",
                        reply_markup=inline_kb1)
                elif response[0] == 401:
                    await msg.message.edit_text(
                        "Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await msg.message.edit_text("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
        else:
            button_api = InlineKeyboardButton(text='➕ Добавить API', callback_data='api_add')
            button_balance = InlineKeyboardButton(text='💰 Баланс', callback_data='balance')
            button_support = InlineKeyboardButton(text='👨🏻\u200d💻 Поддержка', url="https://t.me/roboticselleradmin")
            LK = InlineKeyboardMarkup(row_width=2).add(button_api, button_balance, button_support)
            await msg.message.edit_text("У вас не указан API ключ!", reply_markup=LK)
    else:
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
        await msg.message.delete()
    await DB_user(user_id, msg.data)


# ____________________________________________________________


# ________________Setup Price_________________________________
@dp.callback_query_handler(Text(startswith="Setup_Last_"), state="*")
async def Edit_Last_callback(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        nm = msg.data.split("Setup_Last_")[1]
        nm_s = nm
        user_id = msg.from_user.id
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    loop23 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    passed = 0
                    start_nm = msg.data.split("Edit_Next_")
                    for nm in nms:
                        if str(nm_s) == str(nm):
                            l = len(nms) - 1 - loop23
                            passed = 1
                        if passed == 1:
                            if l != loop:
                                passed = 1
                                if loop >= 6:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm}",
                                                                            callback_data=f'setup_{nm}')
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Setup_Next_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Setup_Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, last, next)
                                    elif loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm}",
                                                                            callback_data=f'setup_{nm}')
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Setup_Next_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Setup_Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last, next)
                                    break
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                                elif loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                    loop1 = 0
                                    # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                            else:
                                if loop1 == 1:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Setup_Next_{nm}')
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, next)
                                elif loop1 == 2:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Setup_Next_{nm}')
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, next)
                                break
                        loop23 = loop23 + 1
                        loop1 = loop1 + 1
                        loop = loop + 1
                    inline_kb1.add(InlineKeyboardButton(f"Назад",
                                                        callback_data=f'Set_Standart_Sale'))
                    await msg.message.edit_text(
                        "Выберите артикул, на который нужно установить новую цену",
                        reply_markup=inline_kb1)
                    await DB_user(user_id, last_message="Выбор в меню артиклов")
                elif response[0] == 401:
                    await msg.message.answer("Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="Setup_Next_"), state="*")
async def Edit_Next_callback(msg: types.CallbackQuery):
    user_id = msg.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        nm = msg.data.split("Setup_Next_")[1]
        nm_s = nm
        inl = msg.message.reply_markup.inline_keyboard
        loop = 0
        start_nm = 0
        passed = 0
        for i in inl:
            for a in i:
                text = a.text.split()[0]
                callback_data = a.callback_data
                if text != f"все":
                    passed = 1
                    start_nm = a.text.split()[0]
                    break
            if passed == 1:
                break
        user_id = msg.from_user.id
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    loop23 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    passed = 0
                    for nm in nms:
                        if passed == 1:
                            if l != loop:
                                if loop >= 6:
                                    if loop1 == 1:
                                        inline_btn_1 = InlineKeyboardButton(f"{nm}",
                                                                            callback_data=f'setup_{nm}')
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Setup_Next_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Setup_Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, last, next)
                                    elif loop1 == 2:
                                        inline_btn_2 = InlineKeyboardButton(f"{nm}",
                                                                            callback_data=f'setup_{nm}')
                                        next = InlineKeyboardButton(f"➡️", callback_data=f'Setup_Next_{nm}')
                                        last = InlineKeyboardButton(f"⬅️", callback_data=f"Setup_Last_{start_nm}")
                                        inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last, next)
                                    break
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}",
                                                                        callback_data=f'setup_{nm}')
                                elif loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}",
                                                                        callback_data=f'setup_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                    loop1 = 0
                                    # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                            else:
                                if loop1 == 1:
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}",
                                                                        callback_data=f'setup_{nm}')
                                    last = InlineKeyboardButton(f"⬅️", callback_data=f"Setup_Last_{start_nm}")
                                    inline_kb1 = inline_kb1.add(inline_btn_1, last)
                                if loop1 == 2:
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}",
                                                                        callback_data=f'setup_{nm}')
                                    last = InlineKeyboardButton(f"⬅️", callback_data=f"Setup_Last_{start_nm}")
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, last)
                            loop = loop + 1
                            loop1 = loop1 + 1
                        if str(nm) == str(nm_s):
                            passed = 1
                            l = len(nms) - loop23 - 1
                        loop23 = loop23 + 1
                    inline_kb1.add(InlineKeyboardButton(f"Назад",
                                                        callback_data=f'Set_Standart_Sale'))
                    await msg.message.edit_text(
                        "Выберите артикул, на который нужно установить новую цену",
                        reply_markup=inline_kb1)
                    await DB_user(user_id, last_message="Выбор в меню артиклов")
                elif response[0] == 401:
                    await msg.message.answer("Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await msg.message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.delete()
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="setup_"), state="*")
async def Edit_Next_callback(msg: types.CallbackQuery, state: FSMContext):
    user_id = msg.from_user.id
    nm = msg.data.split("setup_")[1]
    answer = await DB_get_key(user_id)
    await state.finish()
    if answer is not None:
        headers = {
            'Authorization': answer,
        }
        async with aiohttp.ClientSession() as session:
            response = await Get_Info(headers, session)
            if response[0] == 200:
                for info in response[1]:
                    if int(info.get("nmId")) == int(nm):
                        nm_sale = info.get("price")
                        sale = info.get("discount")
                        cost = nm_sale - (float(sale) / 100 * nm_sale)
                        backs = InlineKeyboardButton(text='Назад', callback_data="Setup_menu")
                        key = InlineKeyboardMarkup().add(backs)
                        await msg.message.edit_text(
                            f'<i>Артикул</i> <code>{nm}\n</code>Текущая цена без скидки – <b>{nm_sale}₽\n</b>Текущая цена после скидки – <b>{cost}₽ ({sale}%)</b>\n\nВведите новую цену <b>до скидки</b>:',
                            reply_markup=key, parse_mode="HTML")
                        await states.setup_get.set()
                        await state.update_data(nm=nm, message_id=msg.message.message_id, chat_id=msg.message.chat.id)
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.message_handler(state=states.setup_get)
async def edit_callback(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await DB_user(user_id, message.text)
    a = await state.get_data()
    msg_id = a.get('message_id')
    chat_id = a.get("chat_id")
    a = a.get("nm")
    text = message.text
    if "%" in text:
        pass
    else:
        try:
            int(text)
        except:
            await message.answer("Некорректное значение.")
            return
    try:
        headers = {
            'Authorization': await DB_get_key(user_id),
        }
        async with aiohttp.ClientSession() as session:
            response = await Get_Info(headers, session)
            if response[0] == 200:
                for inf in response[1]:
                    if int(inf.get("nmId")) == int(a):
                        nm_sale = inf.get("discount")
                        sales = text
                        break
            elif response[0] == 401:
                await message.answer("Api ключ не верен!")
            elif response[0] == 500:
                await message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
        cost = int(text) - (float(nm_sale) / 100 * int(text))
        cost = str(int(cost))
        await message.delete()
        button_api = InlineKeyboardButton(text='Да, установить', callback_data='Setup_yes')
        button_balance = InlineKeyboardButton(text='Назад', callback_data=f'setup_{a}')
        key = InlineKeyboardMarkup().add(button_api, button_balance)
        msg_id = await bot.edit_message_text(
            text=f"Подтверждаете установку цены <b>{text}₽</b> (<b>{cost}₽ после текущей скидки {nm_sale}%</b>) на артикул <code>{a}</code>??",
            message_id=msg_id,
            chat_id=chat_id, parse_mode="HTML", reply_markup=key)
        await state.update_data(nm=a, cost=text, sale=cost, sales=nm_sale)
        await states.setup_accept.set()
    except Exception as e:
        print(e)


@dp.callback_query_handler(Text(startswith="Setup_yes"), state="*")
async def edit_yes_callback(msg: types.CallbackQuery, state: FSMContext):
    user_id = msg.from_user.id
    a = await state.get_data()
    await state.finish()
    if a != {}:
        sale = a.get("sale")
        nm = a.get("nm")
        cost = a.get("cost")
        sales = a.get("sales")
        headers = {
            'Authorization': await DB_get_key(user_id),
        }
        async with aiohttp.ClientSession() as session:
            response = await Get_Info(headers, session)
            if response[0] == 200:
                payload = [{
                    "nmId": int(nm),
                    "price": int(cost)
                }]
                responses = await Set_Price(headers, session, payload)
                if int(responses[0]) == 200:
                    await msg.message.edit_text(
                        f"🟢 Цена <b>{cost}₽</b> (<b>{sale}₽ после текущей скидки {sales}</b>) успешно установлена на артикул <code>{nm}</code>",
                        reply_markup=None, parse_mode="HTML")
                elif int(responses[0]) == 400:
                    backs = InlineKeyboardButton(text='Назад', callback_data=f"setup_{nm}")
                    key = InlineKeyboardMarkup().add(backs)
                    error = responses[1].get("errors")[0].replace(";", '.\n    ')
                    passed = 1
                    temps = []
                    for temp in error.split():
                        if passed == 1:
                            passed = 0
                            temp = "\n" + temp.title()
                        if "." in temp:
                            passed = 1
                        temps.append(temp)
                    await msg.message.edit_text(f"🔴 WB вернул ошибку:\n    {' '.join(temps)}", reply_markup=key)
            elif response[0] == 401:
                await msg.message.edit_text("Api ключ не верен!")
            elif response[0] == 500:
                await msg.message.edit_text("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    else:
        await msg.message.edit_text("Произошла ошибка, попробуйте снова.")
    await msg.answer()
    await DB_user(msg.from_user.id, msg.data)


@dp.callback_query_handler(Text(startswith="Setup_menu"), state="*")
async def Get_articles(msg: types.CallbackQuery, state: FSMContext):
    user_id = msg.from_user.id
    await state.finish()
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    for nm in nms:
                        l = len(nms) - 1
                        if l != loop:
                            if loop >= 6:
                                if loop1 == 1:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Setup_Next_{nm}')
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, next)
                                elif loop1 == 2:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Setup_Next_{nm}')
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, next)
                                break
                            if loop1 == 1:
                                inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                            elif loop1 == 2:
                                inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                                inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                loop1 = 0
                                # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                            loop1 = loop1 + 1
                            loop = loop + 1
                        else:
                            if loop1 == 1:
                                inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                                inline_kb1 = inline_kb1.add(inline_btn_1)
                            if loop1 == 2:
                                inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'setup_{nm}')
                                inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                    inline_kb1.add(InlineKeyboardButton(f"Назад",
                                                        callback_data=f'Set_Standart_Sale'))
                    await msg.message.edit_text(
                        "Выберите артикул, на который нужно установить новую цену",
                        reply_markup=inline_kb1)
                elif response[0] == 401:
                    await msg.message.edit_text(
                        "Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await msg.message.edit_text("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
        else:
            button_api = InlineKeyboardButton(text='➕ Добавить API', callback_data='api_add')
            button_balance = InlineKeyboardButton(text='💰 Баланс', callback_data='balance')
            button_support = InlineKeyboardButton(text='👨🏻\u200d💻 Поддержка', url="https://t.me/roboticselleradmin")
            LK = InlineKeyboardMarkup(row_width=2).add(button_api, button_balance, button_support)
            await msg.message.edit_text("У вас не указан API ключ!", reply_markup=LK)
    else:
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
        await msg.message.delete()
    await DB_user(user_id, msg.data)


@dp.callback_query_handler(Text(startswith="Set_Standart_Sale"), state="*")
async def edit_callback(msg: types.CallbackQuery, state: FSMContext):
    user_id = msg.from_user.id
    Edit_menu = InlineKeyboardButton(text="Установка скидки", callback_data=f'Edit_menu')
    Set_price = InlineKeyboardButton(text='Установка цены', callback_data='Setup_menu')
    LK = InlineKeyboardMarkup(row_width=2).add(Edit_menu, Set_price)
    await msg.message.edit_text("Выберите, что вы хотите поменять", reply_markup=LK)


# ____________________________________________________________________


@dp.message_handler(state=states.set_api)
async def write_API(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        user_id = message.from_user.id
        if len(message.text) >= 120:
            await bot.send_message(admin,
                                   f"Юзер @{message.from_user.username}({message.from_user.id}): Запросил проверку своего ключа.")
            msg = await message.answer("Проверка ключа....")
            headers = {
                'Authorization': message.text,
            }
            await state.finish()
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
            if response[0] == 200:
                answer = await DB_key(user_id, message.text)
                await msg.edit_text("✅ API-ключ успешно подключен")
                await message.answer("Воспользуйтесь кнопкой «Меню» для изменения скидки на товары", reply_markup=None)
            elif response[0] == 401:
                await msg.edit_text("Api ключ не верен!")
            elif response[0] == 500:
                await msg.edit_text("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
        else:
            url = "https://seller.wildberries.ru/supplier-settings/access-to-new-api"
            keyboard = InlineKeyboardMarkup()
            button = InlineKeyboardButton('Ссылка', url=url)
            keyboard.add(button)
            await message.answer(
                "Неверный формат ключа.\nПолучить API ключ можно в личном кабинете поставщика. Перейдите по ссылке ниже для его создания 🔽",
                reply_markup=keyboard)
    else:
        await message.delete()
        await message.answer("Приобретите подписку для продолжения использования бота")
    await DB_user(user_id, message.text)


@dp.message_handler(state=states.edit_sale)
async def edit_callback(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await DB_user(user_id, message.text)
    a = await state.get_data()
    msg_id = a.get('message_id')
    chat_id = a.get("chat_id")
    a = a.get("nm")
    text = message.text
    if "%" in text:
        pass
    else:
        try:
            int(text)
        except:
            await message.answer("Некорректное значение.")
            return
    try:
        headers = {
            'Authorization': await DB_get_key(user_id),
        }
        async with aiohttp.ClientSession() as session:
            response = await Get_Info(headers, session)
            if response[0] == 200:
                for inf in response[1]:
                    if int(inf.get("nmId")) == int(a):
                        nm_sale = inf.get("price")
                        if "%" in text:
                            sales = text.replace("%", "")
                        else:
                            sales = text
                        if int(nm_sale) >= int(sales):
                            pass
                        else:
                            await message.answer(
                                "Невозможно установить конченую стоимость выше стоимости товара. Чтобы поменять стоимость товара воспользуйтесь сайтом WB.")
                            return
                        break
            elif response[0] == 401:
                await message.answer("Api ключ не верен!")
            elif response[0] == 500:
                await message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
        if "%" in text:
            sale = text.replace("%", "")
        else:
            p = 100 / (nm_sale / int(text))
            sale = round(100 - p)
        cost = nm_sale - (float(sale) / 100 * nm_sale)
        cost = str(int(cost))
        await message.delete()
        button_api = InlineKeyboardButton(text='Да, установить', callback_data='edit_yes')
        button_balance = InlineKeyboardButton(text='Назад', callback_data=f'edit_{a}')
        key = InlineKeyboardMarkup().add(button_api, button_balance)
        msg_id = await bot.edit_message_text(
            text=f"Подтверждаете установку скидки <b>{sale}%</b> (<b>{cost}₽</b>) на артикул {a}?", message_id=msg_id,
            chat_id=chat_id, parse_mode="HTML", reply_markup=key)
        await state.update_data(nm=a, sale=sale, cost=cost)
        await states.sale_accept.set()
    except Exception as e:
        print(e)


@dp.callback_query_handler(Text(startswith="Edit_menu"), state="*")
async def Get_articles(msg: types.CallbackQuery, state: FSMContext):
    user_id = msg.from_user.id
    await state.finish()
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    nms = []
                    for info in answer:
                        nm = info.get("nmId")
                        price = info.get("price")
                        discount = info.get("discount")
                        promoCode = info.get("promoCode")
                        nms.append(nm)
                    '''await message.answer(
                        f"Выберите нужные артиклы.\n\n{''.join(nmids)}\n\nВыбери артиклы и пришли мне команду '`/select_articles` Номера артиклов через запятую\n\nПример `/select_articles {nm}, 1234567`'",
                        parse_mode="Markdown")
                    '''
                    loop = 0
                    loop1 = 1
                    inline_kb1 = InlineKeyboardMarkup()
                    inline_kb1.row_width = 2
                    for nm in nms:
                        l = len(nms) - 1
                        if l != loop:
                            if loop >= 6:
                                if loop1 == 1:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                    inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, next)
                                elif loop1 == 2:
                                    next = InlineKeyboardButton(f"➡️", callback_data=f'Edit_Next_{nm}')
                                    inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                    inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2, next)
                                break
                            if loop1 == 1:
                                inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                            elif loop1 == 2:
                                inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                                loop1 = 0
                                # last = InlineKeyboardButton(f"Превед. страница", callback_data=f'last_{nm}')
                            loop1 = loop1 + 1
                            loop = loop + 1
                        else:
                            if loop1 == 1:
                                inline_btn_1 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                inline_kb1 = inline_kb1.add(inline_btn_1)
                            if loop1 == 2:
                                inline_btn_2 = InlineKeyboardButton(f"{nm}", callback_data=f'edit_{nm}')
                                inline_kb1 = inline_kb1.add(inline_btn_1, inline_btn_2)
                    inline_kb1.add(InlineKeyboardButton(f"🔁 Установить стандартные значения скидок",
                                                        callback_data=f'Set_Standart_Sale'))
                    await msg.message.edit_text(
                        "Выберите артикул, на который нужно установить новую скидку",
                        reply_markup=inline_kb1)
                elif response[0] == 401:
                    await msg.message.edit_text(
                        "Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
                elif response[0] == 500:
                    await msg.message.edit_text("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
        else:
            button_api = InlineKeyboardButton(text='➕ Добавить API', callback_data='api_add')
            button_balance = InlineKeyboardButton(text='💰 Баланс', callback_data='balance')
            button_support = InlineKeyboardButton(text='👨🏻\u200d💻 Поддержка', url="https://t.me/roboticselleradmin")
            LK = InlineKeyboardMarkup(row_width=2).add(button_api, button_balance, button_support)
            await msg.message.edit_text("У вас не указан API ключ!", reply_markup=LK)
    else:
        await msg.message.answer("Приобретите подписку для продолжения использования бота")
        await msg.message.delete()
    await DB_user(user_id, msg.data)


@dp.message_handler(commands="select_articles")
async def Select_articles(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    passed = await DB_Get_Passed(user_id)
    if passed is True:
        key = message.get_args().split(",")
        answer = await DB_get_key(user_id)
        if answer is not None:
            headers = {
                'Authorization': answer,
            }
            async with aiohttp.ClientSession() as session:
                response = await Get_Info(headers, session)
                if response[0] == 200:
                    answer = response[1]
                    nmids = []
                    error = []
                    nms = []
                    keys = []
                    nm_write = []
                    key1 = []
                    error.append("Такого артикла у вас нет, он не был записан в БД: ")
                    for info in answer:
                        nm = info.get("nmId")
                        discount = info.get("discount")
                        nmids.append(nm)
                        if int(discount) > 5:
                            discountsale = discount - 29
                            if int(discountsale) < 5:
                                discountsale = 5
                        else:
                            discountsale = 5
                        for nm1 in key:
                            nm1 = nm1.strip()
                            if str(nm1) == str(nm):
                                keys.append({
                                    "discount": discountsale,
                                    "nm": nm1
                                })
                                key1.append({
                                    "discount": discount,
                                    "nm": nm1
                                })
                                nm_write.append(f'{nm1}\n')
                                nms.append(f"{nm1},")
                    await DB_nmid_set_key(user_id, keys, key1, "".join(nms))
                    await message.answer(f"Я записал вот эти артиклы:\n{''.join(nm_write)}")
                elif response[0] == 401:
                    await message.answer(
                        f"Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже. Ваш ключ был удален из БД, если вы считаете что это ошибка то напишите Тех админу @{admin_name}")
                    await DB_key(user_id, None)
                    await bot.send_message(admin,
                                           f"У юзера @{message.from_user.username}({user_id}): Был сброшен ключ ```{answer}```")
                elif response[0] == 500:
                    await message.answer("Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
        else:
            await message.answer(
                "У вас не настроен api ключ!\n\nИспользуйте /key api или используйте /key для более подробной информации")
    else:
        await message.delete()
        await message.answer("Приобретите подписку для продолжения использования бота")
    await DB_user(user_id, message.text)


@dp.message_handler(commands="set_5", state='*')
async def Setup_5(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    if str(user_id) == str(admin1):
        await Set_5()
    await DB_user(user_id, message.text)


@dp.message_handler(commands="Set_Standart")
async def Setup_Standart(message: types.Message):
    user_id = message.from_user.id
    if str(user_id) == str(admin1):
        await Set_Standart()
    await DB_user(user_id, message.text)


@dp.message_handler(Text(equals="Назад"), state="*")
async def admin_Back(msg: types.Message, state: FSMContext):
    button_api = InlineKeyboardButton(text='➕ Добавить API', callback_data='api_add')
    button_balance = InlineKeyboardButton(text='💰 Баланс', callback_data='balance')
    button_support = InlineKeyboardButton(text='👨🏻\u200d💻 Поддержка', url="https://t.me/roboticselleradmin")
    LK = InlineKeyboardMarkup(row_width=2).add(button_api, button_balance, button_support)
    await msg.answer("Личный кабинет", reply_markup=LK)
    user_id = msg.from_user.id
    last_message = msg.text
    await DB_user(user_id, last_message)
    await state.finish()


@dp.message_handler(commands="set_money")
async def set_mone(admin_msg: types.Message):
    if str(admin_msg.from_user.id) == str(admin1):
        data = admin_msg.get_args()
        user_id = data.split()[0]
        money = data.split()[1]
        await set_money(int(user_id), int(money))
        await admin_msg.answer(f"Успешно установил {user_id} {money}Р")
    await DB_user(admin_msg.from_user.id, admin_msg.text)


@dp.message_handler(commands="sendall")
async def sendall(admin_msg: types.Message):
    if str(admin_msg.from_user.id) == str(admin1):
        try:
            data = admin_msg.get_args()
            notf = data.split()[0]
            if notf == "1":
                notf = False
                data = data.split(maxsplit=1)[1]
                await MassSend(f'{"".join(data)}', notf)
            elif notf == "0":
                notf = True
                data = data.split(maxsplit=1)[1]
                await MassSend(f'{"".join(data)}', notf)
            else:
                await admin_msg.answer("Укажи notf")
        except Exception as e:
            await admin_msg.answer(f'Error: {e}')
    else:
        user_id = admin_msg.from_user.id
        last_message = admin_msg.text
        await DB_user(user_id, last_message)


@dp.message_handler(commands="subs")
async def subs(admin_msg: types.Message):
    if str(admin_msg.from_user.id) == str(admin1):
        try:
            async with aiosqlite.connect(r"BalanceUser.db") as db:
                cursor = await db.cursor()
                await cursor.execute('SELECT * FROM user_info')
                a = await cursor.fetchall()
                await cursor.execute('SELECT * FROM user_balance')
                a1 = await cursor.fetchall()
                loop = 0
                for user_ids in a:
                    sub = user_ids[3]
                    sub_date = user_ids[4]
                    user_id = user_ids[0]
                    if str(sub) == str(1):
                        loop = loop + 1
                        a = await bot.get_chat(user_id)
                        await admin_msg.answer(
                            f"@{a.username} ({user_id}) Подписка до {datetime.datetime.fromtimestamp(int(sub_date)).strftime('%d.%m.%Y %H:%M')}")
                money = 0
                for user_ids in a1:
                    money = money + int(user_ids[1])
                await admin_msg.answer(f"Всего {loop} человек. На всех балансах {money} р.")
        except Exception as e:
            await admin_msg.answer(f'Error: {e}')
    else:
        user_id = admin_msg.from_user.id
        last_message = admin_msg.text
        await DB_user(user_id, last_message)


@dp.message_handler(commands="sendsubs")
async def sendsubs(admin_msg: types.Message):
    if str(admin_msg.from_user.id) == str(admin1):
        try:
            data = admin_msg.get_args()
            notf = data.split()[0]
            if notf == "1":
                notf = True
                data = data.split(maxsplit=1)[1]
                await MassSendSubs(f'{"".join(data)}', notf)
            elif notf == "0":
                notf = False
                data = data.split(maxsplit=1)[1]
                await MassSendSubs(f'{"".join(data)}', notf)
            else:
                await admin_msg.answer("Укажи notf")
        except Exception as e:
            await admin_msg.answer(f'Error: {e}')
    else:
        user_id = admin_msg.from_user.id
        last_message = admin_msg.text
        await DB_user(user_id, last_message)


@dp.message_handler(commands="count")
async def count(admin_msg: types.Message):
    if str(admin_msg.from_user.id) == str(admin1):
        async with aiosqlite.connect("Users.db") as db:
            async with db.execute("SELECT * FROM User") as cursor:
                allinfo = await cursor.fetchall()
        await admin_msg.answer(f"Пользователей:  {len(allinfo)}")
        await check_sub()
    else:
        user_id = admin_msg.from_user.id
        last_message = admin_msg.text
        await DB_user(user_id, last_message)


@dp.message_handler(commands="send")
async def admin_send(admin_msg: types.Message):
    if int(admin_msg.from_user.id) == int(admin1):
        try:
            data = admin_msg.get_args()
            user_id = data.split()[0]
            text = data.split(maxsplit=1)[1]
            await bot.send_message(user_id, f'{text}')
            a = await dp.bot.get_chat(user_id)
            await admin_msg.answer(f'Send msg: {a.username}({user_id}), text: {text}.')
        except Exception as ex:
            await admin_msg.answer(f'Send msg ERROR: {ex}')
    else:
        user_id = admin_msg.from_user.id
        last_message = admin_msg.text
        await DB_user(user_id, last_message)
        await set_default_commands()


@dp.message_handler(state="*", content_types=types.ContentType.all())
async def inecorect(message: types.__all__):
    messages = message.html_text
    a = []
    a.append(messages)
    await bot.send_message(admin, text=str(a))


async def Update_Discount(headers, session, user_id):
    try:
        response = await Get_Info(headers, session)
        if response[0] == 200:
            answer = await DB_nmid(user_id)
            nm_id = []
            answer_id = answer[2].split(",")
            for a in answer_id:
                if a != "":
                    nm_id.append(a)
            keys = []
            key1 = []
            for r in response[1]:
                nm = r.get("nmId")
                discount = r.get("discount")
                if int(discount) > 5:
                    discountsale = discount - 29
                    if int(discountsale) < 5:
                        discountsale = 5
                else:
                    discountsale = 5
                for n in nm_id:
                    if str(nm) == str(n):
                        keys.append({
                            "discount": discountsale,
                            "nm": nm
                        })
                        key1.append({
                            "discount": discount,
                            "nm": nm
                        })
            await DB_nmid_set_key(user_id, keys, key1, None)
        elif response[0] == 401:
            await bot.send_message(user_id, "Ваш ключ не работает! Пожалуйста получите новый api ключ по ссылке ниже")
        elif response[0] == 500:
            await bot.send_message(user_id, "Простите сервер вернул ошибку на своей стороне, попробуйте позже...")
    except Exception as e:
        await bot.send_message(admin, '')


async def Post_Discount(payload, headers, session, user_id, nm):
    try:
        async with session.post('https://suppliers-api.wildberries.ru/public/api/v1/updateDiscounts', headers=headers,
                                json=payload) as response:
            try:
                if response.status == 200:
                    try:
                        answer = await response.json(content_type=None)
                    except Exception as e:
                        print(e)
                        answer = ' '
                        await bot.send_message(admin, f"{user_id}({e})")
                    try:
                        alreadyExists = answer.get('alreadyExists')
                        if alreadyExists is None:
                            await bot.send_message(user_id,
                                                   f"🟢 Скидка на -30% успешно установлена на артикулы:\n    {nm}",
                                                   disable_notification=True)
                            await bot.send_message(admin,
                                                   f"{user_id}({answer}): Было успешно установленны значения на -30%")
                        else:
                            await bot.send_message(admin, f"{user_id}({answer}): уже установлены")
                    except Exception as e:
                        await bot.send_message(admin, f"{user_id}({e})")
                elif response.status == 400:
                    answer = await response.json(content_type=None)
                    await bot.send_message(admin, f"{user_id}: {answer}")
                elif response.status == 401:
                    await bot.send_message(admin, f"{user_id}: Не правильный Api_key!")
                    await bot.send_message(user_id,
                                           f"Не удалось поставить значение ваших товаров на -30%, причина:\n     У вас не правильный Api ключ, он был сброшен! Устоновите новый ключ командой /key")
                elif response.status == 500:
                    await bot.send_message(admin, f"{user_id}: Ошибка Wilberis API, Перезапустите позже!")
                    await bot.send_message(user_id,
                                           f"Не удалось поставить значение ваших товаров на -30%, причина:\n    Ошибка Wilberis API! Предупредил Тех администратора")
            except aiogram.utils.exceptions.RetryAfter as e:
                await asyncio.sleep(e.timeout)
    except Exception as e:
        print(e, 'Post_Discount')


async def Post_Discount_standart(payload, headers, session, user_id, nm):
    try:
        async with session.post('https://suppliers-api.wildberries.ru/public/api/v1/updateDiscounts', headers=headers,
                                json=payload) as response:
            if response.status == 200:
                try:
                    answer = await response.json(content_type=None)
                except Exception as e:
                    print(e)
                    answer = ' '
                    await bot.send_message(admin, f"{user_id}: {e}")
                try:
                    alreadyExists = answer.get('alreadyExists')
                    if alreadyExists is None:
                        await bot.send_message(user_id,
                                               f"🟢 Стандартные значения успешно возвращены на артикулы:\n    {nm}",
                                               disable_notification=True)
                        await bot.send_message(admin,
                                               f"{user_id}({answer}): Были успешно установленны стандартные значения для товаров!")
                    else:
                        await bot.send_message(admin, f"{user_id}({answer}): уже установлены")
                except Exception as e:
                    await bot.send_message(admin, f"{user_id}: {e}")
            elif response.status == 400:
                answer = await response.json(content_type=None)
                await bot.send_message(admin, f"{user_id}: {answer}")
            elif response.status == 401:
                await bot.send_message(admin, f"{user_id}: Не правильный Api_key!")
                await bot.send_message(user_id,
                                       f"Не удалось поставить стандартные значения ваших товаров, причина:\n     У вас не правильный Api ключ, он был сброшен! Устоновите новый ключ командой /key")
            elif response.status == 500:
                await bot.send_message(admin, f"{user_id}: Ошибка Wilberis API, Перезапустите позже!")
                await bot.send_message(user_id,
                                       f"Не удалось поставить стандартные значения ваших товаров, причина:\n    Ошибка Wilberis API! Предупредил Тех администратора")
            else:
                await bot.send_message(admin, f"{user_id}: {response.status}")
    except Exception as e:
        print(e, 'Post_Discount_standart')
        await bot.send_message(admin, f"ERROR_Standart_1({user_id}):  {e}")


async def Get_Info(headers, session):
    async with session.get('https://suppliers-api.wildberries.ru/public/api/v1/info', headers=headers) as response:
        if response.status != 401:
            answer = await response.json(content_type="text/plain")
            return response.status, answer
        else:
            return response.status, "1"


async def Set_Sale(headers, session, payload):
    async with session.post('https://suppliers-api.wildberries.ru/public/api/v1/updateDiscounts', headers=headers,
                            json=payload) as response:
        if response.status != 401:
            answer = await response.json(content_type="text/plain")
            return response.status, answer
        else:
            return response.status, "1"


async def Set_Price(headers, session, payload):
    async with session.post('https://suppliers-api.wildberries.ru/public/api/v1/prices', headers=headers,
                            json=payload) as response:
        if response.status != 401:
            answer = await response.json(content_type="text/plain")
            return response.status, answer
        else:
            return response.status, "1"


async def Set_5():
    try:
        async with aiosqlite.connect("Users.db") as db:
            async with db.execute("SELECT * FROM User") as cursor:
                allinfo = await cursor.fetchall()
                tasks = []
                tasks1 = []
                print("Открыл сессию")
                session = aiohttp.ClientSession()
                await bot.send_message(admin, f"Открыл сессию!")
                for info in allinfo:
                    user_id = info[0]
                    api_key = info[1]
                    key = info[2]
                    nm = info[6]
                    if nm is not None:
                        nm = info[6].split(",")
                        nm = "\n    ".join(nm)
                        if key is not None and api_key is not None:
                            key = eval(key)
                            headers = {
                                'Authorization': api_key,
                            }
                            try:
                                await Update_Discount(headers, session, user_id)
                                await Post_Discount(key, headers, session, user_id, nm)
                                await asyncio.sleep(0.6)
                            except Exception as e:
                                print(e)
                                await bot.send_message(admin, f"ERROR_Set_5_1: {e} {user_id}")
                    else:
                        pass
                    await asyncio.sleep(2)
    except Exception as e:
        await bot.send_message(admin, f"ERROR_Set_5: {e}")
        await session.close()
        print(e)
    finally:
        if session:
            await session.close()
            print("Закрытие сессии")
            await bot.send_message(admin, f"Закрытие сессии!")


async def Set_Standart():
    try:
        async with aiosqlite.connect("Users.db") as db:
            async with db.execute("SELECT * FROM User") as cursor:
                allinfo = await cursor.fetchall()
                print("Открыл сессию")
                session = aiohttp.ClientSession()
                await bot.send_message(admin, f"Открыл сессию!")
                for info in allinfo:
                    user_id = info[0]
                    key1 = info[3]
                    Api_key = info[1]
                    nm = info[6]
                    if nm is not None:
                        nm = info[6].split(",")
                        nm = "\n    ".join(nm)
                        if key1 is not None and Api_key is not None:
                            key1 = eval(key1)
                            headers = {
                                'Authorization': Api_key,
                            }
                            try:
                                await Post_Discount_standart(key1, headers, session, user_id, nm)
                                await asyncio.sleep(3)
                            except Exception as e:
                                print(e, user_id)
                                await bot.send_message(admin, f"ERROR_Standart_2: {e}  {user_id}")
                        else:
                            pass
                    else:
                        pass

    except Exception as e:
        await bot.send_message(admin, f"ERROR_Standart: {e}")
        print(e)
        await session.close()
    finally:
        if session:
            await session.close()
            await bot.send_message(admin, f"Закрытие сессии!")
            print("Закрытие сессии")


async def check_sub():
    try:
        async with aiosqlite.connect(r"BalanceUser.db") as db:
            cursor = await db.cursor()
            await cursor.execute('SELECT * FROM user_info')
            info = await cursor.fetchall()
            for inf in info:
                user_id = inf[0]
                deposits = inf[1]
                offs = inf[2]
                sub = inf[3]
                sub_date = inf[4]
                if sub != 0:
                    dt = datetime.datetime.fromtimestamp(sub_date)
                    tt = dt.timestamp()
                    now = datetime.datetime.now()
                    now = now.timestamp()
                    if tt <= now:
                        money = await get_money(user_id)
                        if money >= 99:
                            money = money - 99
                            print(user_id, money)
                            await set_money(user_id, money)
                            now = datetime.datetime.now()
                            now = now + datetime.timedelta(days=30)
                            now = now.timestamp()
                            offs = offs.split(",")
                            nows = datetime.datetime.now().strftime("%H:%M %d-%m-%Y")
                            offs.append(f"{nows} - 99₽ \n")
                            await cursor.execute(
                                'INSERT INTO user_info (user_id, deposits, offs, sub, sub_date) VALUES (?, ?, ?, ?, ?)',
                                (user_id, deposits, ",".join(offs), 1, now))
                            await db.commit()
                            await bot.send_message(user_id,
                                                   "Плата 99₽ за ежемесячную подписку успешна списана с баланса ✅", )
                        else:
                            await cursor.execute(
                                'INSERT INTO user_info (user_id, deposits, offs, sub, sub_date) VALUES (?, ?, ?, ?, ?)',
                                (user_id, deposits, offs, 0, None))
                            await db.commit()
                            topup = InlineKeyboardButton("Своя сумма", callback_data="topup")
                            up99 = InlineKeyboardButton("+99₽", callback_data="up99")
                            pay = InlineKeyboardMarkup(row_width=2).add(up99, topup)
                            await bot.send_message(user_id,
                                                   "Срок действия подписки истёк. Чтобы продолжить пользоваться ботом пополните баланс 💳",
                                                   reply_markup=pay)
                else:
                    money = await get_money(user_id)
                    if money is not None:
                        if money >= 99:
                            now = datetime.datetime.now()
                            now = now + datetime.timedelta(days=30)
                            now = now.timestamp()
                            offs = offs.split()
                            nows = datetime.datetime.now().strftime("%H:%M %d-%m-%Y")
                            offs.append(f"{nows} - 99₽ \n")
                            money = money - 99
                            await set_money(user_id, money)
                            await cursor.execute(
                                'INSERT INTO user_info (user_id, deposits, offs, sub, sub_date) VALUES (?, ?, ?, ?, ?)',
                                (user_id, deposits, ",".join(offs), 1, now))
                            await db.commit()
                            await bot.send_message(user_id, "Подписка активна. Бот готов к работе ✅", )
    except Exception as e:
        print(e)
        await bot.send_message(admin, f"{e}")


async def Dump_BD():
    date = datetime.datetime.now()
    await bot.send_message(chat_id=admin, text=f"Ваш дамп повелитель, за {date.strftime('%d %B, %H:%M')}")
    await bot.send_document(chat_id=admin, document=open("Users.db", "rb"))
    await bot.send_document(chat_id=admin, document=open("BalanceUser.db", "rb"))


async def scheduler():
    aioschedule.every(1).seconds.do(check_sub)
    aioschedule.every().day.at("01:00").do(Set_5)
    aioschedule.every().day.at("06:00").do(Set_Standart)
    aioschedule.every().day.at("00:00").do(Dump_BD)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(50)


async def on_startup(_):
    a = await bot.me
    print(a)
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    while True:
        try:
            executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
        except Exception as e:
            time.sleep(15)
            print(e)
