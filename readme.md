# Telegram bot для получения уведоплений о времени лекций и дедлайнах в ШАДе

## Install

* get token from @BotFather
* install firefox
* install gecko driver
* pip3 install requirements.txt

# run
```python
python3 main.py YOUR_TOKEN
```

# configuring
edit config in main.py
    
* [from_hour, to_hour] - интервал в который бот может слать уведомления
* deadline_notify_days - время уведомления (в днях) до дедлайна
* lesson_notify_min - время увеломления (в мин) до начала лекций 
