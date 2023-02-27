import logging
from aiogram import Bot, Dispatcher, executor, types
import argparse
from manytask import get_cpp_deadlines
from lk import get_lk_deadlines, get_lk_lessons
from routes import add_routes
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('token')
    args = parser.parse_args()
    conn = sqlite3.connect('users.db')
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

    executor.start_polling(dp, skip_updates=True)
