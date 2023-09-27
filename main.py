import telebot
from currency_converter import CurrencyConverter

TOKEN = 'YOUR_TOKEN'

bot = telebot.TeleBot(TOKEN)
converter = CurrencyConverter()


@bot.message_handler(commands=['start'])
def start_handler(msg):
    bot.send_message(msg.chat.id, 'Привет! Я бот для конвертации валют 🤖')
    convert_handler(msg)


def get_currency_markup():
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        row_width=2,
        resize_keyboard=True
    )
    markup.add(
        telebot.types.KeyboardButton('RUB->USD'),
        telebot.types.KeyboardButton('RUB->EUR'),
        telebot.types.KeyboardButton('USD->EUR'),
        telebot.types.KeyboardButton('EUR->USD'),
        telebot.types.KeyboardButton('Другое'),
    )
    return markup


def get_yes_no_markup():
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    markup.add(
        telebot.types.KeyboardButton('Да'),
        telebot.types.KeyboardButton('Нет'),
    )
    return markup


@bot.message_handler(commands=['convert'])
def convert_handler(msg):
    bot.send_message(msg.chat.id, 'Напечатай сумму 💸')

    def yes_no_callback(_msg):
        if _msg.text == 'Да':
            convert_handler(_msg)
        elif _msg.text == 'Нет':
            bot.reply_to(_msg, 'Спасибо за использование. Я всегда рад Вам помочь 😊')
        else:
            bot.reply_to(_msg, 'Неизвестная команда 😒')

    def currency_callback(_msg, amount):
        if _msg.text == 'Другое':
            bot.reply_to(_msg, 'Напечатай пару валют в формате XXX->YYY 💱')
            bot.register_next_step_handler(_msg, currency_callback, amount)
        else:
            pair = _msg.text.strip().upper().split('->')
            if len(pair) != 2:
                bot.reply_to(_msg, 'Неправильный формат. Выбери пару валют 💱', reply_markup=get_currency_markup())
                bot.register_next_step_handler(_msg, currency_callback, amount)
            else:
                try:
                    result = converter.convert(amount, pair[0], pair[1])
                    bot.reply_to(_msg, f'Результат: {amount} {pair[0]} = {result:.2f} {pair[1]}')
                    bot.reply_to(_msg, f'Хотите сконвертировать валюту повторно❓', reply_markup=get_yes_no_markup())
                    bot.register_next_step_handler(_msg, yes_no_callback)
                except ValueError:
                    bot.reply_to(_msg, 'Такая валюта не поддерживается. Выбери пару валют 💱',
                                 reply_markup=get_currency_markup())
                    bot.register_next_step_handler(_msg, currency_callback, amount)

    def summa_callback(_msg):
        amount = _msg.text.strip()
        if not amount.isnumeric():
            bot.reply_to(_msg, 'Неправильный формат. Напечатай сумму 💸')
            bot.register_next_step_handler(_msg, summa_callback)
        else:
            amount = int(amount)
            bot.reply_to(_msg, 'Выбери пару валют 💱', reply_markup=get_currency_markup())
            bot.register_next_step_handler(_msg, currency_callback, amount)

    bot.register_next_step_handler(msg, summa_callback)


@bot.message_handler(commands=['author'])
def author_handler(msg):
    bot.reply_to(msg, 'Автор бота: @ivanstasevich')


def main():
    print('Polling...')
    bot.infinity_polling()


if __name__ == '__main__':
    main()
