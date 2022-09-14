import requests
import telebot
from telebot import types, custom_filters
import json
import config
from telebot.handler_backends import State, StatesGroup #States
from telebot.storage import StateMemoryStorage


class States(StatesGroup):
    s_start = State()
    s_experience = State()
    s_schedule = State()
    s_data = State()
    s_salary = State()
    s_city = State()
    s_vacancy = State()
    s_contin = State()
    s_answer = State()


state_storage = StateMemoryStorage()

bot = telebot.TeleBot(config.token, state_storage=state_storage)
params = {'text': 'Data Scientist',
              'area': '113',
              'type': 'open',
              'per_page': '5',
              'page': '0',
              'period': 7
              }

class Vacancy():
    def __init__(self, page):
        self.page = page
        keys = ['expirience', 'schedule', 'salary', 'city']

        for key in keys:
            self.key = None



    @bot.message_handler(commands=['start', 'help'])
    def get_experience(message):
        markup = types.InlineKeyboardMarkup()
        zero = types.InlineKeyboardButton(text='Нет опыта', callback_data='noExperience')
        one = types.InlineKeyboardButton(text='От 1 года до 3 лет', callback_data='between1And3')
        three = types.InlineKeyboardButton(text='От 1 года до 3 лет', callback_data='between3And6')
        six = types.InlineKeyboardButton(text='Более 6 лет', callback_data='moreThan6')
        markup.add(zero, one)
        markup.add(three, six)

        send_mess = f"<b>Привет, {message.from_user.first_name}</b>!\nПриступим к поиску вакансий!"
        bot.send_message(message.chat.id, send_mess, parse_mode='html')

        bot.send_message(message.chat.id, 'Выберите опыт работы', parse_mode='html', reply_markup=markup)
        bot.set_state(message.chat.id, States.s_salary)


    @bot.callback_query_handler(func=lambda call: True, state=States.s_salary)
    def get_salary(call):
        params['experience.id'] = call.data
        bot.send_message(call.from_user.id, 'Введите желаемую зарплату')
        bot.set_state(call.from_user.id, States.s_schedule)

    @bot.message_handler(func=lambda m: True, state=States.s_schedule)
    def get_schedule(message):

        params['salary.from']  = message.text
        markup = types.InlineKeyboardMarkup()
        full = types.InlineKeyboardButton(text='Полный день', callback_data='fullDay')
        removable = types.InlineKeyboardButton(text='Сменный график', callback_data='shift')
        flexible = types.InlineKeyboardButton(text='Гибкий график', callback_data='flexible')
        remote = types.InlineKeyboardButton(text='Удаленная работа', callback_data='remote')
        markup.add(full, removable)
        markup.add(flexible, remote)
        bot.send_message(message.chat.id, 'Выберите график работы', reply_markup=markup)
        bot.set_state(message.chat.id, States.s_city)


    def getAreas(message):
        city = requests.get('https://api.hh.ru/areas', {'area': 113})
        data = city.content.decode()
        city.close()
        obj = json.loads(data)
        areas = []
        for k in obj:
            for i in range(len(k['areas'])):
                if len(k['areas'][i]['areas']) != 0:  # Если у зоны есть внутренние зоны
                    for j in range(len(k['areas'][i]['areas'])):
                        areas.append(k['areas'][i]['areas'][j]['name'])
                else:  # Если у зоны нет внутренних зон
                    areas.append(k['areas'][i]['name'])
        return areas

    @bot.callback_query_handler(func=lambda c: True, state=States.s_city)
    def get_city(call):
        params['schedule.id']  = call.data

        bot.send_message(call.from_user.id, 'Введите город')
        bot.set_state(call.from_user.id, States.s_vacancy)

    @bot.message_handler(func=lambda message: True, state=States.s_vacancy)
    def get_vacancies(message):
        n = 0
        params['area.name'] = message.text
        city = message.text
        url = 'https://api.hh.ru/vacancies'
        response = requests.get(url, params)
        json = response.json()

#        for i in json:

        new_json = []
        for irem in json['items']:
            name = irem['name']
            employer = irem['employer']['name']
            area = irem['area']['name']
            alternate_url = irem['alternate_url']

            if irem['salary'] != None:
                if irem['salary']['from'] != None and irem['salary']['to'] != None:
                    salary_from = irem['salary']['from']
                    salary_to= irem['salary']['to']
                    salary = f"{salary_from} - {salary_to}"
                elif irem['salary']['from'] != None and irem['salary']['to'] == None:
                    salary_from = irem['salary']['from']
                    salary = f"от {salary_from}"
                elif irem['salary']['from'] == None and irem['salary']['to'] != None:
                    salary_to = irem['salary']['to']
                    salary = f"до {salary_to}"
            else:
                salary = 'Зарплата не указана'

            vac = {
                #	'id': id,
                    'name': name,
                    'salary': salary,
                    'employer': employer,
                    'area': area,
                    'alternate_url': alternate_url
                    }


            new_json.append(vac)

        vacancies = []
        for lists in new_json:
            for values in lists.values():
                vacancies.append(values)
        list = []
        for i in range(0, len(vacancies), 5):
            list.append(vacancies[i:i+5])


        for item in list:
            for j in item:
                ssilka = item[4]
                vacan = item[:4]

                vacan2 = '\n'.join(map(str, vacan))

            markup = types.InlineKeyboardMarkup()
            url = types.InlineKeyboardButton(text='Подробнее', url=ssilka)
            markup.add(url)

            bot.send_message(message.chat.id, vacan2, reply_markup=markup)

        markup_cont = types.InlineKeyboardMarkup()
        yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        markup_cont.add(yes, no)
        bot.send_message(message.chat.id, 'Начать сначала?', reply_markup=markup_cont)

        bot.set_state(message.chat.id, States.s_answer)

    @bot.callback_query_handler(func=lambda c: True, state=States.s_answer)
    def answer(call):
        if call.data == 'yes':
            bot.delete_state(call.from_user.id)
            bot.send_message(call.from_user.id, 'Нажмите /start')
        else:
            bot.send_message(call.from_user.id, 'До новых встреч!')
            bot.delete_state(call.from_user.id)



bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(non_stop=True)
