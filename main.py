import logging
from aiogram import Bot, Dispatcher, executor, types
import argparse
from manytask import add_manytask
from lk import add_lkdeadline, add_lklessions
from signup import add_signup, add_lksignup, add_manytasksignup
from start import add_start
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
    
    add_start(dp, bot)
    add_signup(dp, bot, conn)
    add_lksignup(dp, bot, conn)
    add_manytasksignup(dp, bot, conn)
    add_manytask(dp, bot, conn)
    add_lklessions(dp, bot, conn)
    add_lkdeadline(dp, bot, conn)

    executor.start_polling(dp, skip_updates=True)
