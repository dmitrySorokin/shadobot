from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def get_credentials(conn, user_id):
    cursor = conn.cursor()
    login, password = cursor.execute(f'SELECT lk_login,lk_password FROM users WHERE user_id = {user_id}').fetchone()
    return login, password


def preproc(txt):
    return re.sub('\s+', ' ', txt.replace('\n', ' ')).strip()


def get_month(txt):
    return {
        'января': 1, 
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12
    }[txt]


def get_session(login, password):
    s = requests.Session()

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    page = driver.get('https://lk.yandexdataschool.ru')
    driver.find_element(By.ID, 'id_username').send_keys(login)
    driver.find_element(By.ID, 'id_password').send_keys(password)
    driver.find_element(By.CLASS_NAME, "btn.btn-primary.sign-up-in").click()

    for cookie in driver.get_cookies():
        s.cookies.update({cookie['name']: cookie['value']})
    driver.close()
    return s


def get_lk_deadlines(conn, user_id):
        login, password = get_credentials(conn, user_id)
        session = get_session(login, password)

        soup = BeautifulSoup(session.get('https://lk.yandexdataschool.ru/learning/assignments/').text, 'html.parser')
        for task in soup.find_all('tr'):
            deadline, task_name, course, status, method = map(lambda item: re.sub('\s+',' ',item.text.replace('\n', ' ')).strip(), task.find_all('td'))
            if status != 'Не сдано':
                continue
            
            deadline = deadline.split(' ')
            if 'сегодня' in deadline:
                dt = datetime(
                    day=datetime.now().day, 
                    month=datetime.now().month, 
                    year=datetime.now().year,
                    hour=int(deadline[1][0:2]), 
                    minute=int(deadline[1][3:5])
                )
            elif 'завтра' in deadline:
                date = datetime.now() + timedelta(days=1)
                dt = datetime(
                    day=date.day, 
                    month=date.month, 
                    year=date.year,
                    hour=int(deadline[1][0:2]), 
                    minute=int(deadline[1][3:5])
                )
            else:
                dt = datetime(
                    day=int(deadline[0]), 
                    month=get_month(deadline[1]), 
                    year=int(deadline[2]),
                    hour=int(deadline[3][0:2]), 
                    minute=int(deadline[3][3:5])
                )
            
            if dt > datetime.now():
                yield {'deadline': dt, 'task': task_name, 'course': course}


def get_lk_lessons(conn, user_id):
        login, password = get_credentials(conn, user_id)
        session = get_session(login, password)

        soup = BeautifulSoup(session.get('https://lk.yandexdataschool.ru/learning/courses/').text, 'html.parser')
        for task in soup.find_all('tr'):
            btn = task.find('a', class_='btn')
            if btn is None or preproc(btn.text) != 'Покинуть курс':
                continue

            href = task.find('a', href=True)
            title, link = preproc(href.text), href['href']
            course_soup = BeautifulSoup(session.get(link + 'classes').text, 'html.parser')
            time_table = course_soup.find('div', id='course-classes')
            if time_table is None:
                continue
            for lesson in time_table.find_all('tr')[1:]: # skip header
                date, lesson_name, *_ = filter(lambda x: len(x), lesson.text.split('\n'))
                dt = datetime(
                    day=int(date[0:2]), 
                    month=get_month(date[3:-11]), 
                    year=datetime.now().year,
                    hour=int(date[-11:-9]), 
                    minute=int(date[-8:-6])
                )

                if dt > datetime.now():
                    yield {'deadline': dt, 'task': 'lesson', 'course': {preproc(lesson_name)}}
