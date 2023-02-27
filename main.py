import logging
from aiogram import Bot, Dispatcher, executor
import argparse
from routes import add_routes
import sqlite3
from schedule import start_notifying

# Configure logging
logging.basicConfig(level=logging.INFO, filename='logs.txt')

CONFIG = {
    'db_name': 'users.db',
    'from_hour': 10,
    'to_hour': 21,
    'deadline_notify_days': 3,
    'lesson_notify_min': 15
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('token')
    args = parser.parse_args()
    conn = sqlite3.connect(CONFIG['db_name'])
    cursor = conn.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS users (\
            user_id integer PRIMARY KEY,\
            lk_login text,\
            lk_password text,\
            manytask_login text,\
            manytask_password text\
        )')
    conn.commit()

    bot = Bot(token=args.token)
    dp = Dispatcher(bot)
    add_routes(dp, bot, conn)

    start_notifying(bot, **CONFIG)

    executor.start_polling(dp, skip_updates=True)
