from manytask import get_cpp_deadlines
from lk import get_lk_deadlines, get_lk_lessons
from common import format_date
from datetime import datetime, timedelta
import threading
import time
import sqlite3
import asyncio
import logging



def update(conn):
    result = {
        'users': dict(),
        'updated': datetime.now(),
    }

    cursor = conn.cursor()
    for (user_id,) in cursor.execute(f'SELECT user_id FROM users').fetchall():
        result['users'][user_id] = dict()
        try:
            result['users'][user_id]['cpp_deadlines'] = list(get_cpp_deadlines(conn, user_id))
        except Exception as e:
            result['users'][user_id]['cpp_deadlines'] = []
            logging.warning('update:get_cpp_deadlines ' + str(e))
        try:
            result['users'][user_id]['lk_deadlines'] = list(get_lk_deadlines(conn, user_id))
        except Exception as e:
            result['users'][user_id]['lk_deadlines'] = []
            logging.warning('update:get_lk_deadlines ' + str(e))
        try:
            result['users'][user_id]['lk_lessons'] = list(get_lk_lessons(conn, user_id))
        except Exception as e:
            result['users'][user_id]['lk_lessons'] = []
            logging.warning('update:get_lk_lessons ' + str(e))

    return result


def _do_notify(bot, db, loop, deadline_notify_days, lesson_notify_min):
    date = datetime.now()
    lesson_notify_delta = timedelta(minutes=lesson_notify_min)
    deadline_notify_delta = timedelta(days=deadline_notify_days)
    logging.info('_do_notify')

    for user_id in db['users']:
        for cpp in db['users'][user_id]['cpp_deadlines']:
            if cpp['deadline'] - date < deadline_notify_delta and 'notified' not in cpp:
                asyncio.ensure_future(bot.send_message(user_id, f'{cpp["task"]} до {format_date(cpp["deadline"])}'), loop=loop)
                cpp['notified'] = date
        
        for lk in db['users'][user_id]['lk_deadlines']:
            if lk['deadline'] - date < deadline_notify_delta and 'notified' not in lk:
                asyncio.ensure_future(bot.send_message(user_id, f'{lk["task"]} до {format_date(lk["deadline"])}'), loop=loop)
                lk['notified'] = date
        
        for lk in db['users'][user_id]['lk_lessons']:
            start = lk['deadline']
            if start - date < lesson_notify_delta and 'notified' not in lk:
                asyncio.ensure_future(bot.send_message(user_id, f'{lk["course"]} начнется в {start.hour}:{start.minute}'), loop=loop)
                lk['notified'] = date


def _notify(bot, loop, db_name, from_hour, to_hour, deadline_notify_days, lesson_notify_min):
    conn = sqlite3.connect(db_name)
    db = update(conn)
    logging.info(db)
    while True:
        date = datetime.now()
        if date.hour < from_hour:
            to_date = datetime(hour=from_hour, day=date.day, month=date.month, year=date.year)
            delta = to_date - date
            logging.info(f'sleep until: {to_date} for: {delta} = {delta.total_seconds()}s')
            time.sleep(delta.total_seconds())
            db = update(conn)
        elif date.hour > to_hour:
            to_date = datetime(hour=from_hour, day=date.day, month=date.month, year=date.year) + timedelta(days=1)
            delta = to_date - date
            logging.info(f'sleep until: {to_date} for: {delta} = {delta.total_seconds()}s')
            time.sleep(delta.total_seconds())
            db = update(conn)
        else:
            _do_notify(bot, db, loop, deadline_notify_days, lesson_notify_min)
            time.sleep(5 * 60)
    

def start_notifying(bot, db_name, from_hour, to_hour, deadline_notify_days, lesson_notify_min):
    loop = asyncio.get_event_loop()
    t = threading.Thread(target=_notify, args=(bot, loop, db_name, from_hour, to_hour, deadline_notify_days, lesson_notify_min), daemon=True)
    t.start()
