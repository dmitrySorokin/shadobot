from aiogram import Bot, Dispatcher, executor, types
from lk import get_lk_deadlines, get_lk_lessons
from manytask import get_cpp_deadlines


def add_routes(dp, bot, conn):
    @dp.message_handler(commands=['start', 'help'])
    async def handler(message: types.Message) -> None:
        await message.answer(
            'Я могу слать уведомления о дедлайнах и занятиях для сайтов lk.yandexdataschool.ru и cpp.manytask.org\n'
            'Используй команды:\n'
            '/info - сохраненные пароли\n'
            '/signlk - добавить пароль для lk.yandexdataschool.ru\n'
            '/signcpp - добавить пароль для cpp.manytask.org\n'
            '/lessons - расписание лекций\n'
            '/lk - дедлайны lk.yandexdataschool.ru\n'
            '/cpp - дедлайны cpp.manytask.org'
        )

    
    @dp.message_handler(commands=['info'])
    async def handle_info(message: types.Message):
        cursor = conn.cursor()
        for user_id, lk_login, lk_password, manytask_login, manytask_password in cursor.execute(
            'SELECT user_id,lk_login,lk_password,manytask_login,manytask_password FROM users').fetchall():
            if message.from_user.id == user_id:
                await bot.send_message(
                    message.from_user.id, 
                    f'Вы зарегистрированы.\nlk: {lk_login} / {lk_password}\nmanytask: {manytask_login} / {manytask_password}')
                
                return
            
        await bot.send_message(
            message.from_user.id, 
            f'Вы не зарегистрированны.'
        )

        conn.commit()


    @dp.message_handler(commands=['signlk'])
    async def handle_signlk(message: types.Message):
        data = message.text.split(' ')
        if len(data) != 3:
            await bot.send_message(message.from_user.id, 'Введите логин пароль в формате: /signlk login password')
            return
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO users (user_id) VALUES ({message.from_user.id})")
        cursor.execute(f"UPDATE users SET lk_login = '{data[1]}', lk_password = '{data[2]}' WHERE user_id = {message.from_user.id}")
        conn.commit()
        await bot.send_message(message.from_user.id, 'ok')


    @dp.message_handler(commands=['signcpp'])
    async def handle_signcpp(message: types.Message):
        data = message.text.split(' ')
        if len(data) != 3:
            await bot.send_message(message.from_user.id, 'Введите логин пароль в формате: /signcpp login password')
            return
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO users (user_id) VALUES ({message.from_user.id})")
        cursor.execute(f"UPDATE users SET manytask_login = '{data[1]}', manytask_password = '{data[2]}' WHERE user_id = {message.from_user.id}")
        conn.commit()
        await bot.send_message(message.from_user.id, 'ok')


    @dp.message_handler(commands=['lk'])
    async def handle_deadlines(message: types.Message):
        try:
            async for item in get_lk_deadlines(conn, message.from_user.id):
                await bot.send_message(message.from_user.id, f"dl: {item['deadline']}, tn: {item['task']}, c: {item['course']}")
        except:
            await bot.send_message(message.from_user.id, f'Пароль не верный. Обновите пароль /signlk')


    @dp.message_handler(commands=['lessons'])
    async def handle_lessons(message: types.Message):
        try: 
            async for item in get_lk_lessons(conn, message.from_user.id):
                await bot.send_message(message.from_user.id, f"date: {item['deadline']}, lesson: {item['course']}")
            else:
                await bot.send_message(message.from_user.id, f"date: {item['deadline']}, lesson: {item['course']}")
        except:
            await bot.send_message(message.from_user.id, f'Пароль не верный. Обновите пароль /signlk')


    @dp.message_handler(commands=['cpp'])
    async def handle_cpp(message: types.Message):
        try:
            async for item in get_cpp_deadlines(conn, message.from_user.id):
                await bot.send_message(message.from_user.id, f"date: {item['deadline']}, task: {item['task']}")
        except Exception as e:
            await bot.send_message(message.from_user.id, f'Пароль не верный. Обновите пароль /signcpp')

