# -*- coding: utf-8 -*-
"""ALLRealBot.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1V608LWBG4403BSM3iVgp46JAoqjaCiL_
"""

!pip install pyTelegramBotApi

"""#bot"""

import requests
from urllib.parse import urlencode, quote_plus

class Kinopoisk():
	def __init__(self, api_key):
		self.keywords = None
		self.headers = {'accept': 'application/json', 'X-API-KEY': api_key}
		self.host = 'https://kinopoiskapiunofficial.tech'
		self.path = None
		self.method = None
		self.params = {}

	def search(self, text, film = True, actor = False):
		if actor:
			return self.search_actor(text)
		elif film:
			return self.search_film(text)

	def search_actor(self, text):
		person = self.get_person(text)

		if person and len(person['items']):
			url = {}
			url['path'] = '/api/v1/'
			url['method'] = 'staff/' + str(person['items'][0]['kinopoiskId'])
			url['params'] = None
			actor = self._request(url)
			# print(actor)
			films = []
			for i in actor.get('films')[0:5]:
				if i.get('nameRu'):
					films.append(i.get('nameRu') + " (" + str(i.get('rating', '-')) + ")")
				# films.append(i['nameRu'])

			obj = {
				'id': str(actor.get('personId','-')),
				'name': str(actor.get('nameRu','-')),
				'films': films,
				'posterUrl': str(actor.get('posterUrl','-')),
				'kinlink': str(actor.get('webUrl','-'))
			}
		else:
			obj = None
		return obj

	def search_film(self, text):
		film = self.get_film(text)
		count = self.get_film_count(text)
		# print(count)
		if film:
			staff = self.get_staff(film['filmId'])
			director = self.get_director(staff)
			actors = self.get_actors(staff)

			obj = {
				'count': count,
				'id': film['filmId'],
				'name': film.get('nameRu', film['nameEn']),
				'year': film['year'],
				'country': self.get_country(film['countries']),
				'rating': film.get('rating'),
				'director': director,
				'actors': actors,
				'description': film.get('description'),
				'link': 'https://www.kinopoisk.ru/film/' + str(film['filmId']),
				'photo': film['posterUrl']
			}
		else:
			obj = None
		return obj

	def _request(self, url):
		if url['params']:
			url_str = self.host + url['path'] + url['method'] + "?" + urlencode(url['params'])
		else:
			url_str = self.host + url['path'] + url['method']

		res = requests.get(url_str, headers = self.headers)
		return res.json()

	def get_film(self, film_name):
		url = {}
		url['path'] = '/api/v2.1/films/'
		url['method'] = 'search-by-keyword'
		url['params'] = {'keyword': film_name, 'page': '1'}
		result = self._request(url)
		return result['films'][0] if len(result['films']) else None

	def get_film_count(self, film_name):
		url = {}
		url['path'] = '/api/v2.2/'
		url['method'] = 'films'
		url['params'] = {'order': 'RATING', 'type': 'ALL', 'ratingFrom': '0', 'ratingTo': '10', 'yearFrom': '1000', 'yearTo': '3000', 'keyword': film_name}
		result = self._request(url)
		print(result)
		return len(result['items'])

	def get_staff(self, film_id):
		url = {}
		url['path'] = '/api/v1/'
		url['method'] = 'staff'
		url['params'] = {'filmId': int(film_id)}
		result = self._request(url)
		return result if result else None

	def get_person(self, name):
		url = {}
		url['path'] = '/api/v1/'
		url['method'] = 'persons'
		url['params'] = {'name': name}
		result = self._request(url)
		return result if result else None

	def get_country(self, countries):
		lst_country = []
		for c in countries:
			lst_country.append(c.get('country'))
		return lst_country if lst_country else None

	def get_director(self, staff):
		director = None
		for s in staff:
			if s['professionKey'] == 'DIRECTOR':
				director = s.get('nameRu')
				break
		return director if director else None

	def get_actors(self, staff):
		actors = []
		cnt = 6
		for s in staff:
			if s['professionKey'] == 'ACTOR' and cnt:
				actors.append(s.get('nameRu'))
				cnt -= 1
		return actors if actors else None

import requests
from urllib.parse import urlencode, quote_plus
import telebot
from telebot import types
import pandas as pd
import re
import random

helper = '/start-- перезапускает бота\n\nКнопки  ⬇️⬇️⬇️\n●  Фильм/Сериал--выводит по вашему запросу Фильм/Сериал, что вам нужен!\n●  Cлучайный фильм/сериал--если вам нечего посмотреть, то воспользуйтесь этой кнопкой и ищите то, что вам понравится\n●  Актер--выводит по вашему запросу Актер/Актриссу, что вам нужен\n●  Случайный Актер--если вы хотите познакомиться с новым Актером/Актриссой, то воспользуйтесь этой кнопкой и ищите фильмы с их участием!'
qq = '🎬 *Как бесплатно смотреть фильмы и сериалы на «КиноПоиске»*\n\n1️⃣ Заходим на официальный сайт «Кинопоиска».\n2️⃣ Выбираем фильм или сериал → переходим на страницу.\n3️⃣ После «www.» в адресной строке меняем "kino" на "ss".\n└Должно получиться так — «sspoisk».\n4️⃣ Переходим по адресу → открываем плеер.'

data = pd.read_csv('/content/drive/MyDrive/TELEBOT/Flicks_Bot/kinopoisk-top250.csv', sep=',')
client = telebot.TeleBot('..........')

kino = Kinopoisk('4161ef6d-9f70-4103-918e-84efc60ec86e')
# film = kino.search("Матрица")
# actor = kino.search("Киану Ривз", actor=True)
# print(film, actor)

def clear_msg(text):
	text = text.replace(' ', '').lower()
	text = text.replace(';', '')
	text = text.replace(',', '')
	text = text.replace('ё', 'е')
	text = text.replace('Ё', 'е')
	return text


def clean_link(link):
	link = link.replace("'", '')
	return link





#                                                 ПРИВЕТСТВИЕ+ДОБАВЛЕНИЕ КНОПОК

@client.message_handler(func=lambda c: c.text == '/start')
def start(message):
	mess=f'Привет, {message.from_user.first_name}, Что хотите посмотреть?!'
	client.send_message(message.chat.id, mess, parse_mode='html')
	markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
	btn_start=types.InlineKeyboardButton('/start')
	btn_movie_ser=types.InlineKeyboardButton('Фильм/Сериал')
	btn_rnd_movie=types.InlineKeyboardButton('Cлучайный фильм/сериал')
	btn_rnd_actor=types.InlineKeyboardButton('Cлучайный актер')
	btn_actor=types.InlineKeyboardButton('Актер')
	KPoisk=types.InlineKeyboardButton('Как смотреть бесплатно???')
	FF=types.InlineKeyboardButton('Канал сообщества')
	markup.add(btn_movie_ser, btn_actor)
	markup.add(btn_rnd_movie, btn_rnd_actor)
	markup.add(FF)
	markup.row(KPoisk)
	client.send_message(message.chat.id, '👋', reply_markup=markup)

#                                                ФУНКЦИЯ(КНОПКА) РАНДОМНЫЙ ФИЛЬМ
@client.message_handler(func=lambda c: c.text == "Cлучайный фильм/сериал")
def rand(message):
	name = random.choice(data['movie'])
	for i in range(len(data)):
		if clear_msg(name) == clear_msg(data['movie'][i]):
			client.send_message(message.chat.id, f"●  Название: [{data.loc[i][1].replace(';', ',')}]({clean_link(data.loc[i][9])})\n●  Год: {data.loc[i][2]}\n●  Страна: {data.loc[i][3]}\n●  Рейтинг: {round(data.loc[i][4], 2)}\n●  Режиссер: {data.loc[i][6].replace(';', ',')}\n●  Оператор: {data.loc[i][7].replace(';', ',')}\n●  Актеры: {data.loc[i][8].replace(';', ',')}\n●  Описание: {data.loc[i][5].replace(';', '')}\n●  Кинопоиск: https://www.kinopoisk.ru/film/{re.sub('[^0-9]', '', data.loc[i][9].replace('_', ' '))[3:]} ", parse_mode='Markdown')



#                      РАНДОМНЫЕ АКТЕРЫ
@client.message_handler(func=lambda c: c.text == "Как смотреть бесплатно???")
def kino(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEXjJiSwfIw1ah_TA_UvVJpESIffzeoQACOwMAArVx2gYYSwbSVVPLRCME')      # ИСПРАВЬ
	client.send_message(message.chat.id, qq)

@client.message_handler(func=lambda c: c.text == "Фильм/Сериал")
def film_ser(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEYgABYkyX0Kr38I_YdHOwiricZqzI4MoAAvgSAAJCTllKAAFziHtpqojNIwQ')
	client.send_message(message.chat.id, 'Приготовь вкусняшек!\nНапишите полное название фильма/сериала...\n⬇️⬇️⬇')       # ИСПРАВЬ

@client.message_handler(func=lambda c: c.text == "/help")
def help(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEXqhiSxYKOT32r_p8GIlLxTkee_QCQgACJyAAAulVBRjTVPZqymtoFyME')       # ИСПРАВЬ И ТЕКСТ В СТРОЧКЕ 50 ТОЖЕ СКОПИРУЙ
	client.send_message(message.chat.id, 'Запутались в кнопках?\n\n●  Фильм/Сериал--выводит по вашему запросу Фильм/Сериал, что вам нужен!\n●  Cлучайный фильм/сериал--если вам нечего посмотреть, то воспользуйтесь этой кнопкой и ищите то, что вам понравится.\n●  Актер--выводит по вашему запросу Актера/Актриссу, что вам нужен.\n●  Случайный Актер--если вы хотите познакомиться с новым Актером/Актриссой, то воспользуйтесь этой кнопкой и ищите фильмы с их участием!')


@client.message_handler(func=lambda c: c.text == "Канал сообщества")
def chan(message):
	client.send_message(message.chat.id, ' @flicksbar ')


@client.message_handler(func=lambda c: c.text == "Егор Прилепин")
def EP(message):
	client.send_message(message.chat.id, ' ТОП ')


# @client.message_handler(func=lambda c: c.text == "Андрей Теплов")
# def ANDR(message):
# 	client.send_message(message.chat.id, ' @openeyes_ai_bot ')

@client.message_handler(func=lambda c: c.text == "Авторы")
def author(message):
	client.send_message(message.chat.id, 'Компания DataNateLab\nПо всем вопросам писать ⤵\n@rfs910 или @egorprileppa')


@client.message_handler(func=lambda c: c.text == "Cлучайный актер")
def acrtist(message):
	st_act = []
	for i in range(len(data)):
		st_act.append(data['actors'][i].split(';'))
	set_actors = list(set([x for l in st_act for x in l]))
	act = random.choice(set_actors)
	actor = f"Фильмы, в которых играл(а) {act}\n⬇️⬇️⬇️"
	client.send_message(message.chat.id, actor, parse_mode='html')
	for i in range(len(data)):
		if clear_msg(act) in clear_msg(data['actors'][i]):
			client.send_message(message.chat.id,
			                    f"Название: {data.loc[i][1].replace(';', ',')}\nРейтинг: {round(data.loc[i][4], 2)}")


@client.message_handler(func=lambda c: c.text == "Актер")
def acrtist__1(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEYadiTH_B6nbGGJCzxkPXPqbSlieFxgACQQIAAs4XpwuAhLkjXAPfNSME')
	what_actor = 'Введите полное имя актера/актрисы...\n⬇️⬇️⬇'
	client.send_message(message.chat.id, what_actor, parse_mode='html')


#                                                         РАСПОЗНОВАНИЕ ФИЛЬМОВ

@client.message_handler(content_types=["text"])
def start(message):
	found = False
	kino = Kinopoisk('4161ef6d-9f70-4103-918e-84efc60ec86e')
	film = kino.search(message.text)

	if film and film['count']:
		found = True
		client.send_message(message.chat.id, 'Выполняется поиск...')
		client.send_message(message.chat.id,
		                    f"●  Название: [{film['name']}]({film['photo']})\n●  Год: {film['year']}\n●  Страна: {', '.join(film['country'])}\n●  Рейтинг: {film['rating']}\n●  Режиссер: {film['director']}\n●  Актеры: {', '.join(film['actors'])}\n●  Описание: {film['description']}\n●  Кинопоиск: {film['link']}",
		                    parse_mode='Markdown')
	# print(*film['actors'],sep=', ')
	# print(film)
	else:
		actor = kino.search(message.text, actor=True)
		if actor:
			found = True
			client.send_message(message.chat.id, f"●  Имя: [{actor['name']}]({actor['posterUrl']})\n●  Фильмы: {', '.join(actor['films'])}\n●  Кинопоиск: {actor['kinlink']}",parse_mode='Markdown')

	if not found:
		client.send_message(message.chat.id, "Я не понял ваш запрос!")


print('start')
client.polling(none_stop=True)

"""#bot2"""

import requests
from urllib.parse import urlencode, quote_plus
import telebot
from telebot import types
import pandas as pd
import re
import random





data = pd.read_csv('/content/drive/MyDrive/TELEBOT/kinopoisk-top250.csv', sep=',')
#client = telebot.TeleBot('5294600538:AAGOtmbhU-vE0Of-RW1EyA8UnraQfgPVPwk')
#client = telebot.TeleBot('5126685086:AAGf6kEigUgt-Vf8ZsMW0L6VW-h_KUtgAPg')
client = telebot.TeleBot('5313478178:AAGXKypiaFEg-2yN0oSdOnmk7oWO08wVW0A')



qq='🎬 Как бесплатно смотреть фильмы и сериалы на «КиноПоиске»\n1️⃣ Заходим на официальный сайт «Кинопоиска».\n2️⃣ Выбираем фильм или сериал → переходим на страницу.\n3️⃣ После «www.» в адресной строке меняем "kino" на "ss".\n└Должно получиться так — «sspoisk».\n4️⃣ Переходим по адресу → открываем плеер.'

kino = Kinopoisk('4161ef6d-9f70-4103-918e-84efc60ec86e')


def clear_msg(text):
	text = text.replace(' ', '').lower()
	text = text.replace(';', '')
	text = text.replace(',', '')
	text = text.replace('ё', 'е')
	text = text.replace('Ё', 'е')
	return text

def clean_link(link):
	link = link.replace("'", '')
	return link

#                                                 ПРИВЕТСТВИЕ+ДОБАВЛЕНИЕ КНОПОК

@client.message_handler(func=lambda c: c.text == '/start')
def start(message):
	mess = f'Привет, {message.from_user.first_name}, Что хотите посмотреть?!'
	client.send_message(message.chat.id, mess, parse_mode='html')
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	btn_start = types.InlineKeyboardButton('/start')
	btn_movie_ser = types.InlineKeyboardButton('Фильм/Сериал')
	btn_rnd_movie = types.InlineKeyboardButton('Cлучайный фильм/сериал')
	btn_rnd_actor = types.InlineKeyboardButton('Cлучайный актер')
	btn_actor = types.InlineKeyboardButton('Актер')
	KPoisk = types.InlineKeyboardButton('Как смотреть бесплтано?')
	#autor = types.InlineKeyboardButton('Авторы')
	markup.add(btn_movie_ser, btn_actor)
	markup.add(btn_rnd_movie, btn_rnd_actor)
	#markup.add(aautor)
	markup.row(KPoisk)
	#client.send_message(message.chat.id, '👋', reply_markup=markup)
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEuSVif7lG5qHSnR3-OxoDp7_ExQnH9AAChwIAAladvQpC7XQrQFfQkCQE')




#                                                ФУНКЦИЯ(КНОПКА) РАНДОМНЫЙ ФИЛЬМ
@client.message_handler(func=lambda c: c.text == "Cлучайный фильм/сериал")
def rand(message):
	name = random.choice(data['movie'])
	for i in range(len(data)):
		if clear_msg(name) == clear_msg(data['movie'][i]):
			client.send_message(message.chat.id,
			                    f"●  Название: [{data.loc[i][1].replace(';', ',')}]({clean_link(data.loc[i][9])})\n●  Год: {data.loc[i][2]}\n●  Страна: {data.loc[i][3]}\n●  Рейтинг: {round(data.loc[i][4], 2)}\n●  Режиссер: {data.loc[i][6].replace(';', ',')}\n●  Оператор: {data.loc[i][7].replace(';', ',')}\n●  Актеры: {data.loc[i][8].replace(';', ',')}\n●  Описание: {data.loc[i][5].replace(';', '')}\n●  Кинопоиск: https://www.kinopoisk.ru/film/{re.sub('[^0-9]', '', data.loc[i][9].replace('_', ' '))[3:]} ",
			                    parse_mode='Markdown')
		# client.send_message(message.chat.id, '🎬  Бесплатный просмотр: https://www.sspoisk.ru/film/' + (
		# re.findall(r'\d+', data.loc[i][9].replace('_', ' '))[1]) + '/')


                                                             # РАНДОМНЫЕ АКТЕРЫ
@client.message_handler(func=lambda c: c.text == "Как смотреть бесплтано?")
def kino(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEXjJiSwfIw1ah_TA_UvVJpESIffzeoQACOwMAArVx2gYYSwbSVVPLRCME')      # ИСПРАВЬ
	client.send_message(message.chat.id, '🎬 *Как бесплатно смотреть фильмы и сериалы на «КиноПоиске»*\n\n1️⃣ Заходим на официальный сайт «Кинопоиска».\n2️⃣ Выбираем фильм или сериал → переходим на страницу.\n3️⃣ После «www.» в адресной строке меняем "kino" на "ss".\n└Должно получиться так — «sspoisk».\n4️⃣ Переходим по адресу → открываем плеер.' , parse_mode = 'Markdown')


@client.message_handler(func=lambda c: c.text == "Фильм/Сериал")
def film_ser(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEYgABYkyX0Kr38I_YdHOwiricZqzI4MoAAvgSAAJCTllKAAFziHtpqojNIwQ')
	client.send_message(message.chat.id, 'Приготовь вкусняшек!\nНапишите полное название фильма/сериала...\n⬇️⬇️⬇')       # ИСПРАВЬ
	#client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEYgABYkyX0Kr38I_YdHOwiricZqzI4MoAAvgSAAJCTllKAAFziHtpqojNIwQ')


@client.message_handler(func=lambda c: c.text == "/help")
def help(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEXqhiSxYKOT32r_p8GIlLxTkee_QCQgACJyAAAulVBRjTVPZqymtoFyME')       # ИСПРАВЬ И ТЕКСТ В СТРОЧКЕ 50 ТОЖЕ СКОПИРУЙ
	client.send_message(message.chat.id, 'Запутались в кнопках?\n\n●  Фильм/Сериал--выводит по вашему запросу Фильм/Сериал, что вам нужен!\n●  Cлучайный фильм/сериал--если вам нечего посмотреть, то воспользуйтесь этой кнопкой и ищите то, что вам понравится.\n●  Актер--выводит по вашему запросу Актера/Актриссу, что вам нужен.\n●  Случайный Актер--если вы хотите познакомиться с новым Актером/Актриссой, то воспользуйтесь этой кнопкой и ищите фильмы с их участием!\n●  Авторы--Если вам нужен подобный бот...')


@client.message_handler(func=lambda c: c.text == "Авторы")
def author(message):
	client.send_message(message.chat.id, 'Компания DataNateLab\nПо всем вопросам писать ⤵\n@rfs910 или @egorprileppa')


@client.message_handler(func=lambda c: c.text == "Cлучайный актер")
def acrtist(message):
	st_act = []
	for i in range(len(data)):
		st_act.append(data['actors'][i].split(';'))
	set_actors = list(set([x for l in st_act for x in l]))
	act = random.choice(set_actors)
	actor = f"Фильмы, в которых играл(а) {act}\n⬇️⬇️⬇️"
	client.send_message(message.chat.id, actor, parse_mode='html')
	for i in range(len(data)):
		if clear_msg(act) in clear_msg(data['actors'][i]):
			client.send_message(message.chat.id,
			                    f"Название: {data.loc[i][1].replace(';', ',')}\nРейтинг: {round(data.loc[i][4], 2)}")


@client.message_handler(func=lambda c: c.text == "Актер")
def acrtist__1(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEYadiTH_B6nbGGJCzxkPXPqbSlieFxgACQQIAAs4XpwuAhLkjXAPfNSME')
	what_actor = 'Введите полное имя актера/актрисы...\n⬇️⬇️⬇'
	client.send_message(message.chat.id, what_actor, parse_mode='html')


#                                                         РАСПОЗНОВАНИЕ ФИЛЬМОВ

@client.message_handler(content_types=["text"])
def start(message):
	found = False
	kino = Kinopoisk('4161ef6d-9f70-4103-918e-84efc60ec86e')
	film = kino.search(message.text)
	print('film', film)

	if film and film['count']:
		found = True
		client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEbrdiUv_CNui9QB_oX7uh6ZK4IwABhdIAAicAAyBHKxQLt5zWb8ZYwSME')
		#client.send_message(message.chat.id, 'Выполняется поиск...')
		client.send_message(message.chat.id,
		                    f"●  Название: [{film['name']}]({film['photo']})\n●  Год: {film['year']}\n●  Страна: {', '.join(film['country'])}\n●  Рейтинг: {film['rating']}\n●  Режиссер: {film['director']}\n●  Актеры: {', '.join(film['actors'])}\n●  Описание: {film['description']}\n●  Кинопоиск: {film['link']}",
		                    parse_mode='Markdown')
	# print(*film['actors'],sep=', ')
	# print(film)
	else:
		actor = kino.search(message.text, actor=True)
		print('actor', actor)
		if actor:
			found = True
			client.send_message(message.chat.id, f"●  Имя: [{actor['name']}]({actor['posterUrl']})\n●  Фильмы: {', '.join(actor['films'])}",parse_mode='Markdown')     # \n●  Кинопоиск: {actor['kinlink']}

	if not found:
		client.send_message(message.chat.id, "Я не понял ваш запрос!")


print('start')
client.polling(none_stop=True)

import requests
from urllib.parse import urlencode, quote_plus
import telebot
from telebot import types
import pandas as pd
import re
import random

helper = '/start-- перезапускает бота\n\nКнопки  ⬇️⬇️⬇️\n●  Фильм/Сериал--выводит по вашему запросу Фильм/Сериал, что вам нужен!\n●  Cлучайный фильм/сериал--если вам нечего посмотреть, то воспользуйтесь этой кнопкой и ищите то, что вам понравится\n●  Актер--выводит по вашему запросу Актер/Актриссу, что вам нужен\n●  Случайный Актер--если вы хотите познакомиться с новым Актером/Актриссой, то воспользуйтесь этой кнопкой и ищите фильмы с их участием!'
qq = '🎬 *Как бесплатно смотреть фильмы и сериалы на «КиноПоиске»*\n\n1️⃣ Заходим на официальный сайт «Кинопоиска».\n2️⃣ Выбираем фильм или сериал → переходим на страницу.\n3️⃣ После «www.» в адресной строке меняем "kino" на "ss".\n└Должно получиться так — «sspoisk».\n4️⃣ Переходим по адресу → открываем плеер.'

data = pd.read_csv('/content/drive/MyDrive/TELEBOT/kinopoisk-top250.csv', sep=',')
client = telebot.TeleBot('5313478178:AAGXKypiaFEg-2yN0oSdOnmk7oWO08wVW0A')

kino = Kinopoisk('4161ef6d-9f70-4103-918e-84efc60ec86e')

def clear_msg(text):
	text = text.replace(' ', '').lower()
	text = text.replace(';', '')
	text = text.replace(',', '')
	text = text.replace('ё', 'е')
	text = text.replace('Ё', 'е')
	return text


def clean_link(link):
	link = link.replace("'", '')
	return link







#                                                 ПРИВЕТСТВИЕ+ДОБАВЛЕНИЕ КНОПОК

@client.message_handler(func=lambda c: c.text == '/start')
def start(message):
	mess = f'Привет, {message.from_user.first_name}, Что хотите посмотреть?!'
	client.send_message(message.chat.id, mess, parse_mode='html')
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	btn_start = types.InlineKeyboardButton('/start')
	btn_movie_ser = types.InlineKeyboardButton('Фильм/Сериал')
	btn_rnd_movie = types.InlineKeyboardButton('Cлучайный фильм/сериал')
	btn_rnd_actor = types.InlineKeyboardButton('Cлучайный актер')
	btn_actor = types.InlineKeyboardButton('Актер')
	KPoisk = types.InlineKeyboardButton('Как смотреть бесплтано?')
	autor = types.InlineKeyboardButton('Авторы')
	FF = types.InlineKeyboardButton('Официальный Канал сообщества @flicksbar ')
	markup.add(btn_movie_ser, btn_actor)
	markup.add(btn_rnd_movie, btn_rnd_actor)
	markup.add(FF)

	markup.row(KPoisk)
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEuSVif7lG5qHSnR3-OxoDp7_ExQnH9AAChwIAAladvQpC7XQrQFfQkCQE')


#                                                ФУНКЦИЯ(КНОПКА) РАНДОМНЫЙ ФИЛЬМ
@client.message_handler(func=lambda c: c.text == "Cлучайный фильм/сериал")
def rand(message):
	name = random.choice(data['movie'])
	for i in range(len(data)):
		if clear_msg(name) == clear_msg(data['movie'][i]):
			client.send_message(message.chat.id,
			                    f"●  Название: [{data.loc[i][1].replace(';', ',')}]({clean_link(data.loc[i][9])})\n●  Год: {data.loc[i][2]}\n●  Страна: {data.loc[i][3]}\n●  Рейтинг: {round(data.loc[i][4], 2)}\n●  Режиссер: {data.loc[i][6].replace(';', ',')}\n●  Оператор: {data.loc[i][7].replace(';', ',')}\n●  Актеры: {data.loc[i][8].replace(';', ',')}\n●  Описание: {data.loc[i][5].replace(';', '')}\n●  Кинопоиск: https://www.kinopoisk.ru/film/{re.sub('[^0-9]', '', data.loc[i][9].replace('_', ' '))[3:]} ",
			                    parse_mode='Markdown')
		# client.send_message(message.chat.id, '🎬  Бесплатный просмотр: https://www.sspoisk.ru/film/' + (
		# re.findall(r'\d+', data.loc[i][9].replace('_', ' '))[1]) + '/')


                                                             # РАНДОМНЫЕ АКТЕРЫ
@client.message_handler(func=lambda c: c.text == "Как смотреть бесплтано?")
def kino(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEXjJiSwfIw1ah_TA_UvVJpESIffzeoQACOwMAArVx2gYYSwbSVVPLRCME')      # ИСПРАВЬ
	client.send_message(message.chat.id, '🎬 *Как бесплатно смотреть фильмы и сериалы на «КиноПоиске»*\n\n1️⃣ Заходим на официальный сайт «Кинопоиска».\n2️⃣ Выбираем фильм или сериал → переходим на страницу.\n3️⃣ После «www.» в адресной строке меняем "kino" на "ss".\n└Должно получиться так — «sspoisk».\n4️⃣ Переходим по адресу → открываем плеер.' , parse_mode = 'Markdown')


@client.message_handler(func=lambda c: c.text == "Фильм/Сериал")
def film_ser(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEYgABYkyX0Kr38I_YdHOwiricZqzI4MoAAvgSAAJCTllKAAFziHtpqojNIwQ')
	client.send_message(message.chat.id, 'Приготовь вкусняшек!\nНапишите полное название фильма/сериала...\n⬇️⬇️⬇')       # ИСПРАВЬ
	#client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEYgABYkyX0Kr38I_YdHOwiricZqzI4MoAAvgSAAJCTllKAAFziHtpqojNIwQ')


@client.message_handler(func=lambda c: c.text == "/help")
def help(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEXqhiSxYKOT32r_p8GIlLxTkee_QCQgACJyAAAulVBRjTVPZqymtoFyME')       # ИСПРАВЬ И ТЕКСТ В СТРОЧКЕ 50 ТОЖЕ СКОПИРУЙ
	client.send_message(message.chat.id, 'Запутались в кнопках?\n\n●  Фильм/Сериал--выводит по вашему запросу Фильм/Сериал, что вам нужен!\n●  Cлучайный фильм/сериал--если вам нечего посмотреть, то воспользуйтесь этой кнопкой и ищите то, что вам понравится.\n●  Актер--выводит по вашему запросу Актера/Актриссу, что вам нужен.\n●  Случайный Актер--если вы хотите познакомиться с новым Актером/Актриссой, то воспользуйтесь этой кнопкой и ищите фильмы с их участием!\n●  Авторы--Если вам нужен подобный бот...')


@client.message_handler(func=lambda c: c.text == "Авторы")
def author(message):
	client.send_message(message.chat.id, 'Компания DataNateLab\nПо всем вопросам писать ⤵\n@rfs910 или @egorprileppa')


@client.message_handler(func=lambda c: c.text == "Cлучайный актер")
def acrtist(message):
	st_act = []
	for i in range(len(data)):
		st_act.append(data['actors'][i].split(';'))
	set_actors = list(set([x for l in st_act for x in l]))
	act = random.choice(set_actors)
	actor = f"Фильмы, в которых играл(а) {act}\n⬇️⬇️⬇️"
	client.send_message(message.chat.id, actor, parse_mode='html')
	for i in range(len(data)):
		if clear_msg(act) in clear_msg(data['actors'][i]):
			client.send_message(message.chat.id,
			                    f"Название: {data.loc[i][1].replace(';', ',')}\nРейтинг: {round(data.loc[i][4], 2)}")


@client.message_handler(func=lambda c: c.text == "Актер")
def acrtist__1(message):
	client.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEEYadiTH_B6nbGGJCzxkPXPqbSlieFxgACQQIAAs4XpwuAhLkjXAPfNSME')
	what_actor = 'Введите полное имя актера/актрисы...\n⬇️⬇️⬇'
	client.send_message(message.chat.id, what_actor, parse_mode='html')


#                                                         РАСПОЗНОВАНИЕ ФИЛЬМОВ

@client.message_handler(content_types=["text"])
def start(message):
	found = False
	kino = Kinopoisk('4161ef6d-9f70-4103-918e-84efc60ec86e')
	film = kino.search(message.text)
	print('film', film)

	if film and film['count']:
		found = True
		client.send_message(message.chat.id, 'Выполняется поиск...')
		client.send_message(message.chat.id,
		                    f"●  Название: [{film['name']}]({film['photo']})\n●  Год: {film['year']}\n●  Страна: {', '.join(film['country'])}\n●  Рейтинг: {film['rating']}\n●  Режиссер: {film['director']}\n●  Актеры: {', '.join(film['actors'])}\n●  Описание: {film['description']}\n●  Кинопоиск: {film['link']}",
		                    parse_mode='Markdown')
	# print(*film['actors'],sep=', ')
	# print(film)
	else:
		actor = kino.search(message.text, actor=True)
		print('actor', actor)
		if actor:
			found = True
			client.send_message(message.chat.id, f"●  Имя: [{actor['name']}]({actor['posterUrl']})\n●  Фильмы: {', '.join(actor['films'])}\n●  Кинопоиск: {actor['kinlink']}",parse_mode='Markdown')

	if not found:
		client.send_message(message.chat.id, "Я не понял ваш запрос!")


# for i in range(len(data)):
# 	if clear_msg(message.text) == clear_msg(data['movie'][i]):
# 		found = True
# 		client.send_message(message.chat.id,
# 		                    f"●  Название: [{data.loc[i][1].replace(';', ',')}]({clean_link(data.loc[i][9])})\n●  Год: {data.loc[i][2]}\n●  Страна: {data.loc[i][3]}\n●  Рейтинг: {round(data.loc[i][4], 2)}\n●  Режиссер: {data.loc[i][6].replace(';', ',')}\n●  Оператор: {data.loc[i][7].replace(';', ',')}\n●  Актеры: {data.loc[i][8].replace(';', ',')}\n●  Описание: {data.loc[i][5].replace(';', '')}\n●  Кинопоиск: https://www.kinopoisk.ru/film/{re.sub('[^0-9]', '', data.loc[i][9].replace('_',' '))[3:]} ",
# 		                    parse_mode='Markdown')
# 		# client.send_message(message.chat.id, '🎬  Бесплатный просмотр: https://www.sspoisk.ru/film/' + (
# 		# re.findall(r'\d+', data.loc[i][9].replace('_', ' '))[1]) + '/')
#
# 	elif clear_msg(message.text) in clear_msg(data['actors'][i]):
# 		found = True
# 		client.send_message(message.chat.id, f"Название: {data.loc[i][1]}\nРейтинг: {round(data.loc[i][4], 2)}")
#
#
# if not found:
# 	client.send_message(message.chat.id, "Я не понял ваш запрос!")
#
# client.send_message(message.chat.id, 'test')
# print(kino_res)

print('start')
client.polling(none_stop=True)