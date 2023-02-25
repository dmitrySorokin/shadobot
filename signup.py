import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types


def add_signup(dp, bot, conn):
    @dp.message_handler(commands=['info'])
    async def handle(message: types.Message):
        cursor = conn.cursor()
        for user_id, lk_login, lk_password, manytask_login, manytask_password in cursor.execute(
            'SELECT user_id,lk_login,lk_password,manytask_login,manytask_password FROM users').fetchall():
            if message.from_user.id == user_id:
                await bot.send_message(
                    message.from_user.id, 
                    f'Вы зарегистрированы lk: {lk_login}/{lk_password}, manytask: {manytask_login}/{manytask_password}')
                
                return
            
        await bot.send_message(
            message.from_user.id, 
            f'Вы не зарегистрированны.'
        )

        conn.commit()


def add_lksignup(dp, bot, conn):
    @dp.message_handler(commands=['signlk'])
    async def handle(message: types.Message):
        data = message.text.split(' ')
        if len(data) != 3:
            await bot.send_message(message.from_user.id, 'Введите логин пароль в формате: /signlk login password')
            return
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO users (user_id) VALUES ({message.from_user.id})")
        cursor.execute(f"UPDATE users SET lk_login = '{data[1]}', lk_password = '{data[2]}' WHERE user_id = {message.from_user.id}")
        conn.commit()
        await bot.send_message(message.from_user.id, 'ok')


def add_manytasksignup(dp, bot, conn):
    @dp.message_handler(commands=['signcpp'])
    async def handle(message: types.Message):
        data = message.text.split(' ')
        if len(data) != 3:
            await bot.send_message(message.from_user.id, 'Введите логин пароль в формате: /signcpp login password')
            return
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO users (user_id) VALUES ({message.from_user.id})")
        cursor.execute(f"UPDATE users SET manytask_login = '{data[1]}', manytask_password = '{data[2]}' WHERE user_id = {message.from_user.id}")
        conn.commit()
        await bot.send_message(message.from_user.id, 'ok')
