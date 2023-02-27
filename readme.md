# Telegram bot для получения уведоплений о времени лекций и дедлайнах в ШАДе

## About
Бот парсит данные из личного кабинета lk.yandexdataschool.ru и с сайта cpp.manytask.org для отправки уведомлений о времени лекций и дедлайнах заданий.

## Install

* get token from @BotFather
* install Firefox
* install gecko driver
* pip3 install requirements.txt

## Run
```python
python3 main.py YOUR_TOKEN
```

## Configuring
edit config in main.py
    
* [from_hour, to_hour] - интервал в который бот может слать уведомления
* deadline_notify_days - время уведомления (в днях) до дедлайна
* lesson_notify_min - время увеломления (в мин) до начала лекций 
