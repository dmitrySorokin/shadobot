from bs4 import BeautifulSoup
import requests
from datetime import datetime
from aiogram import Bot, Dispatcher, executor, types


def get_credentials(conn, user_id):
    cursor = conn.cursor()
    login, password = cursor.execute(f'SELECT manytask_login,manytask_password FROM users WHERE user_id = {user_id}').fetchone()
    return login, password


def get_cpp_deadlines(conn, user_id):
    login, password = get_credentials(conn, user_id)
    s = requests.Session()

    res = s.get('https://gitlab.manytask.org/users/sign_in')
    soup = BeautifulSoup(res.text, 'html.parser')
    token = soup.find('input', {'name':'authenticity_token'})['value']
    cookies = res.cookies


    data = {
        'authenticity_token': token,
        'user[login]': login,
        'user[password]': password,
        'user[remember_me]': '0'
    }


    res = s.post('https://gitlab.manytask.org/users/sign_in', data=data)
    res = s.get('https://cpp.manytask.org/login')
    soup = BeautifulSoup(res.text, 'html.parser')
    login_finish_url = soup.find('a', href=True)['href']
    res = s.get(login_finish_url)

    soup = BeautifulSoup(res.text, 'html.parser')
    for group in soup.find_all("div", class_="group"):
        deadline = group.find('div', class_='deadline').text
        # deadline = '[100%: 19-02-2023 23:59 MSK]'
        dt = datetime(
            day=int(deadline[7:9]), 
            month=int(deadline[10:12]), 
            year=int(deadline[13:17]), 
            hour=int(deadline[18:20]), 
            minute=int(deadline[21:23])
        )

        for task in group.find_all('div', class_='task unsolved'):
            if dt > datetime.now():
                yield {'deadline': dt, 'task': task.find('div', class_='name').text, 'course': 'cpp'}
