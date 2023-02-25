from aiogram import Bot, Dispatcher, executor, types


def add_start(dp, bot):
    @dp.message_handler(commands=['start', 'help'])
    async def handler(message: types.Message) -> None:
        await message.answer(
            'Я могу слать уведомления о дедлайнах и занятиях для сайтов lk.yandexdataschool.ru и cpp.manytask.org\n'
            'Используй команды:\n'
            '/info - сохраненные пароли\n'
            '/signlk - добавить пароль для lk.yandexdataschool.ru\n'
            '/signcpp - добавить пароль для cpp.manytask.org\n'
            '/lessons - для получения расписания\n'
            '/lk - дедлайны lk.yandexdataschool.ru\n'
            '/cpp - дедлайны cpp.manytask.org'
        )
