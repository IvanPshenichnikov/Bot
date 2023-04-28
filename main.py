from youtube_search import YoutubeSearch

import requests
from bs4 import BeautifulSoup

import datetime
import random

from googletrans import Translator

from aiogram import Bot, types, utils
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import *

from aiogram.utils.exceptions import NetworkError

import hashlib
import logging

import time

import re
import os

import yt_dlp
from yt_dlp.utils import DownloadError

logging.basicConfig(level=logging.INFO)

bot = Bot(token='TOKEN BOTA', parse_mode='html')
dp = Dispatcher(bot)


class FilenameCollectorPP(yt_dlp.postprocessor.common.PostProcessor):
    def __init__(self):
        super(FilenameCollectorPP, self).__init__(None)
        self.filenames = []

    def run(self, information):
        self.filenames.append(information["filepath"])
        return [], information


# параметры
class Settings:
    def __init__(self):
        self.url = ''
        self.url_id = ''
        self.user_id = ''

        self.views = {1: [1, ''],
                      2: [1, ''],
                      3: [1, ''],
                      4: [1000, 'K'],
                      5: [1000, 'K'],
                      6: [1000, 'K'],
                      7: [1000000, 'M'],
                      8: [1000000, 'M'],
                      9: [1000000, 'M'],
                      10: [1000000000, 'B'],
                      11: [1000000000, 'B'],
                      12: [1000000000, 'B']}

        self.users = {}


settings = Settings()


def text_translator(text='', src='ru', dest='en'):
    translator = Translator()
    translation = translator.translate(text=text, src=src, dest=dest)

    return translation.text


def load_picture():
    try:
        video = f'https://img.youtube.com/vi/{settings.url_id}/maxresdefault.jpg'
        stream = f'https://img.youtube.com/vi/{settings.url_id}/maxresdefault_live.jpg'

        url = settings.url

        result = re.search(r'watch\?v=([a-zA-Z0-9]*)', url)

        if result:
            t_url = None
            video_id = result.group()[0]

            req = requests.get(url)
            page = req.content.decode('utf-8')
            if stream.format(video_id) in page:
                t_url = stream.format(video_id)
            else:
                t_url = video.format(video_id)

            req = requests.get(t_url)

            with open(f'{settings.url_id}.jpg', 'wb') as file:
                file.write(req.content)
                file.close()

            file_size = os.stat(f'{settings.url_id}.jpg').st_size

            if file_size / 1024 < 2:
                os.remove(f'{settings.url_id}.jpg')
                raise IndexError

    except IndexError:
        video = f'https://img.youtube.com/vi/{settings.url_id}/hqdefault.jpg'
        stream = f'https://img.youtube.com/vi/{settings.url_id}/hqdefault_live.jpg'

        url = settings.url

        result = re.search(r'watch\?v=([a-zA-Z0-9]*)', url)

        if result:
            t_url = None
            video_id = result.group()[0]

            req = requests.get(url)
            page = req.content.decode('utf-8')
            if stream.format(video_id) in page:
                t_url = stream.format(video_id)
            else:
                t_url = video.format(video_id)

            req = requests.get(t_url)

            with open(f'{settings.url_id}.jpg', 'wb') as file:
                file.write(req.content)
                file.close()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    settings.users[message.from_user.id] = ['', '', 'en', '', '']
    markup = types.InlineKeyboardMarkup(row_width=2)

    english = types.InlineKeyboardButton('🇬🇧 English', callback_data='startlangeng')
    russian = types.InlineKeyboardButton('🇷🇺 Русский', callback_data='startlangrus')

    markup.add(english, russian)

    await bot.send_message(message.chat.id, '<b>Choose language (Выберите язык).</b>', reply_markup=markup)


@dp.message_handler(commands=['restart'])
async def restart(message: types.Message):
    settings.users[message.from_user.id] = ['', '', 'en', '', '']
    markup = types.InlineKeyboardMarkup(row_width=2)

    english = types.InlineKeyboardButton('🇬🇧 English', callback_data='startlangeng')
    russian = types.InlineKeyboardButton('🇷🇺 Русский', callback_data='startlangrus')

    markup.add(english, russian)

    await bot.send_message(message.chat.id, '<b>Choose language (Выберите язык).</b>', reply_markup=markup)


@dp.message_handler(commands=['language'])
async def language(message: types.Message):
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)

        english = types.InlineKeyboardButton('🇬🇧 English', callback_data='eng')
        russian = types.InlineKeyboardButton('🇷🇺 Русский', callback_data='rus')

        markup.add(english, russian)

        await bot.send_message(message.chat.id,
                               text_translator(text="Выберите язык", src="ru",
                                               dest=settings.users[message.from_user.id][2]),
                               reply_markup=markup)

    except KeyError:
        await message.reply("<b>The bot has been updated and needs to be restarted (Бот обновился и требует перезапуска"
                            ").\n\n"
                            "👉 /restart 👈</b>")


@dp.message_handler(commands=['help'])
async def info(message: types.Message):
    try:
        await bot.send_message(message.chat.id,
                               '<b>{}</b>\n\n🔸 {}\n\n<b>{}</b>'.
                               format(text_translator(
                                   text="Как выбрать и скачать видеоролик с ютуба в аудио и видео формат"
                                        "ах?", src="ru", dest=settings.users[message.from_user.id][2]),

                                      text_translator(
                                          text="Вставьте ссылку на нужный вам видеоролик или воспользуйтесь вну"
                                               "тренним поисковиком.", src="ru",
                                          dest=settings.users[message.from_user.id][2]),

                                      text_translator(
                                          text="На данный момент лимит скачивания - 50 мб., но в скором времени"
                                               " он достигнет 1.5 Гб.", src="ru",
                                          dest=settings.users[message.from_user.id][2]), ))
    except KeyError:
        await message.reply("<b>The bot has been updated and needs to be restarted (Бот обновился и требует перезапуска"
                            ").\n\n"
                            "👉 /restart 👈</b>")


@dp.message_handler(content_types=['text'])
async def text(message: types.Message):
    try:
        if message.text.lower() == 'поиск видео' or message.text.lower() == 'video search':
            markup1 = types.InlineKeyboardMarkup(row_width=1)

            choose = types.InlineKeyboardButton(text_translator(text="Искать видеоролик", src="ru", dest=settings.
                                                                users[message.from_user.id][2]),
                                                switch_inline_query_current_chat='')
            markup1.add(choose)
            await message.reply(text_translator(text="<b>Поисковик</b>", src="ru", dest=settings.
                                                users[message.from_user.id][2]), reply_markup=markup1)

        elif 'youtu' in message.text and '/' not in message.text[0]:
            if 'https://www.youtube.com/watch?v=' in message.text and message.text != \
                    'https://www.youtube.com/watch?v=':
                if '&' in message.text:
                    settings.url_id = message.text[message.text.find('=') + 1:message.text.find('&')]
                else:
                    settings.url_id = message.text[message.text.find('=') + 1:]
                settings.url = f'https://www.youtube.com/watch?v={settings.url_id}'

            elif 'youtube.com/shorts/' in message.text:

                if 'https://youtube.com/shorts/' in message.text and message.text != 'https://youtube.com/shorts/':
                    settings.url_id = message.text[message.text.find('shorts/') + 7:message.text.find('?feature')]

                elif 'https://www.youtube.com/shorts/' in message.text and message.text != \
                        'https://www.youtube.com/shorts/':
                    settings.url_id = message.text[message.text.find('shorts/') + 7:]
                    settings.url = f'https://www.youtube.com/watch?v={settings.url_id}'

            elif 'https://youtu.be/' in message.text and message.text != 'https://youtu.be/':
                settings.url_id = message.text[message.text.find('/') + 11:]
                settings.url = f'https://www.youtube.com/watch?v={settings.url_id}'

            elif 'https://www.youtube.com/live/' in message.text and message.text != 'https://www.youtube.com/live/':
                settings.url_id = message.text[message.text.find('live/') + 5:]
                settings.url = f'https://www.youtube.com/watch?v={settings.url_id}'

            else:
                raise TypeError

            youtube_dl_opts = {
                'ignoreerrors': True,
                'quiet': True
            }

            settings.users[message.from_user.id][0] = settings.url

            load_picture()

            with yt_dlp.YoutubeDL(youtube_dl_opts) as ydl:
                try:
                    try:
                        video = ydl.extract_info(f"ytsearch:{settings.users[message.from_user.id][0]}",
                                                 download=False)['entries'][0]
                    except IndexError:
                        video = ydl.extract_info(f"ytsearch:https://www.youtube.com/watch?v={settings.url_id}",
                                                 download=False)['entries'][0]

                    time = video.get("duration", '00:00:00')
                    duration = datetime.datetime.utcfromtimestamp(time).strftime('%H:%M:%S')

                    if int(int(time) / 60 / 60 / 24) > 0:
                        duration_days = str(int(int(video.get("duration", None)) / 60 / 60 / 24)) + ':'
                    else:
                        duration_days = ''

                    views = video.get("view_count", text_translator(text="Просмотры скрыты.", src="ru",
                                                                    dest=settings.users[message.from_user.id][2]))
                    title = video.get("title", '')

                    settings.users[message.from_user.id][1] = title

                    for i in title:
                        if i in '\/:*?"<>|':
                            settings.users[message.from_user.id][1] = title.replace(i, '')

                    settings.user_id = message.from_user.id

                    like = video.get("like_count", text_translator(text="Лайки скрыты.", src="ru",
                                                                   dest=settings.users[message.from_user.id][2]))
                    autor = video.get("channel", text_translator(text="Название канала скрыто.", src="ru",
                                                                 dest=settings.users[message.from_user.id][2]))
                    up_date = video.get("upload_date", text_translator(text="Дата скачивания скрыта.", src="ru",
                                                                       dest=settings.users[message.from_user.id][2]))
                    upload_date = []

                    for i in up_date:
                        upload_date.append(i)

                    upload_date.insert(-2, '.')
                    upload_date.insert(-5, '.')
                    upload_date = ''.join(upload_date)

                    try:
                        if len(str(like)) > 3:
                            like = str(round(int(like) / settings.views[len(str(like))][0], 1)) + \
                                   settings.views[len(str(like))][1]
                    except ValueError:
                        like = str(like)

                    try:
                        if len(str(views)) > 3:
                            views = str(round(int(views) / settings.views[len(str(views))][0], 1)) + \
                                    settings.views[len(str(views))][1]
                    except ValueError:
                        like = str(like)

                    markup = types.InlineKeyboardMarkup(row_width=3)

                    choose = types.InlineKeyboardButton(text_translator(text="Поиск похожего видео", src="ru",
                                                                        dest=settings.users[message.from_user.id][
                                                                            2]),
                                                        switch_inline_query_current_chat=settings.users
                                                        [message.from_user.id][1])

                    audio = types.InlineKeyboardButton('🔊 ' + text_translator(
                        text="Аудио", src="ru", dest=settings.users[message.from_user.id][2]),
                                                       callback_data='audio')

                    cancel = types.InlineKeyboardButton('❌ ' + text_translator(
                        text="Отмена", src="ru", dest=settings.users[message.from_user.id][2]),
                                                        callback_data='cancel')

                    if not 'short' in message.text:

                        video240 = types.InlineKeyboardButton('🎥 240p', callback_data='video240')
                        video360 = types.InlineKeyboardButton('🎥 360p', callback_data='video360')
                        video480 = types.InlineKeyboardButton('🎥 480p', callback_data='video480')
                        video720 = types.InlineKeyboardButton('🎥 720p', callback_data='video720')
                        video1080 = types.InlineKeyboardButton('🎥 1080p', callback_data='video1080')

                        markup.add(video240, video360, video480, video720, video1080)
                        markup.add(audio)
                        markup.add(cancel, choose)

                    else:

                        video240 = types.InlineKeyboardButton('🎥 240p', callback_data='shortvideo240')
                        video360 = types.InlineKeyboardButton('🎥 360p', callback_data='shortvideo360')
                        video480 = types.InlineKeyboardButton('🎥 480p', callback_data='shortvideo480')
                        video720 = types.InlineKeyboardButton('🎥 720p', callback_data='shortvideo720')
                        video1080 = types.InlineKeyboardButton('🎥 1080p', callback_data='shortvideo1080')

                        markup.add(video240, video360, video480, video720, video1080)
                        markup.add(audio)
                        markup.add(cancel, choose)

                    await bot.send_photo(chat_id=message.chat.id,
                                         photo=open(f'{settings.url_id}.jpg', 'rb'),
                                         caption="<b>{}\n\n"
                                                 "👤 {}\n"
                                                 "👁 {}\n"
                                                 "👍 {}\n"
                                                 "📥 {}\n"
                                                 "🕒 {}{}\n\n"
                                                 '{}'
                                                 '</b>'.format(settings.users[message.from_user.id][1], autor, views,
                                                               like,
                                                               upload_date, duration_days, duration,
                                                               text_translator(text="В каком формате скачать?",
                                                                               src="ru",
                                                                               dest=settings.users[message.from_user.id]
                                                                               [2])), reply_markup=markup)
                except AttributeError:
                    await message.reply(text_translator(
                        text="<b>🚫 Данный видеоролик не доступен.</b>", src="ru",
                        dest=settings.users[message.from_user.id][2]))

                except IndexError:
                    await message.reply(text_translator(
                        text="<b>🚫 Бот не может обработать ссылку, пожалуйста, проверьте наличие "
                             "в ней ошибок.</b>", src="ru",
                        dest=settings.users[message.from_user.id][2]))

                except TypeError:
                    await bot.send_photo(chat_id=message.chat.id,
                                         photo=open(f'{settings.url_id}.jpg', 'rb'),
                                         caption=text_translator(
                                             text="<b>🔴 Это прямой эфир. Скачать не получится.</b>", src="ru",
                                             dest=settings.users[message.from_user.id][2]))

            os.remove(f'{settings.url_id}.jpg')

        else:
            raise TypeError

    except KeyError:
        await message.reply("<b>The bot has been updated and needs to be restarted (Бот обновился и требует перезапуска"
                            ").\n\n"
                            "👉 /restart 👈</b>")

    except TypeError:
        await message.reply(text_translator(text="<b>❗Неправильный ввод. Воспользуйтесь командой /help.</b>", src="ru",
                                            dest=settings.users[message.from_user.id][2]))


@dp.callback_query_handler(lambda call: True)
async def callback(call):
    if call.message:
        try:

            if 'eng' in call.data:
                settings.users[call.message.chat.id][2] = 'en'
                await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                choose_video = types.KeyboardButton(
                    text_translator(text="Поиск видео", src="ru", dest=settings.users[call.message.chat.id][2]))

                markup.add(choose_video)

                await bot.send_message(call.message.chat.id, 'Bot translated into English.', reply_markup=markup)

            if 'rus' in call.data:
                settings.users[call.message.chat.id][2] = 'ru'
                await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                choose_video = types.KeyboardButton(
                    text_translator(text="Поиск видео", src="ru", dest=settings.users[call.message.chat.id][2]))

                markup.add(choose_video)

                await bot.send_message(call.message.chat.id, 'Бот переведён на русский язык.', reply_markup=markup)

            if 'startlang' in call.data:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                choose_video = types.KeyboardButton(
                    text_translator(text="Поиск видео", src="ru", dest=settings.users[call.message.chat.id][2]))

                markup2 = types.InlineKeyboardMarkup(row_width=1)

                choose = types.InlineKeyboardButton(text_translator(text="Искать видеоролик", src="ru", dest=settings.
                                                                    users[call.message.chat.id][2]),
                                                    switch_inline_query_current_chat='')
                markup2.add(choose)
                markup.add(choose_video)
                await bot.send_photo(call.message.chat.id,
                                     open(f'hello_stickers/{random.choice([1, 2, 3, 4, 5, 6, 7, 8])}.jpg', 'rb'),
                                     reply_markup=markup)

                await bot.send_message(
                    call.message.chat.id,
                    '<b>{}</b>\n\n{} \n{}\n\n<b>{}</b>'.format(
                        text_translator(text=f"Приветcтвую! Я - YouTubeBot.",
                                        src="ru", dest=settings.users[call.message.chat.id][2]),
                        text_translator(
                            text=f"С моей помощью вы можете скачать любой видеоролик с YouTube в аудио и видео форматах"
                                 f".", src="ru", dest=settings.users[call.message.chat.id][2]),
                        text_translator(
                            text=f"На данный момент лимит скачивания - 50 мб., но в скором времени он достигнет"
                                 f" 1.5 Гб.",
                            src="ru", dest=settings.users[call.message.chat.id][2]),
                        text_translator(text=f"Воспользуйтесь поисковиком видео или вставьте ссылку на видеоролик.",
                                        src="ru", dest=settings.users[call.message.chat.id][2])), reply_markup=markup2)



            if call.data == 'video240':
                settings.users[call.message.chat.id][4] = '240'
                settings.users[call.message.chat.id][3] = '240'

            if call.data == 'video360':
                settings.users[call.message.chat.id][4] = '360'
                settings.users[call.message.chat.id][3] = '360'

            if call.data == 'video480':
                settings.users[call.message.chat.id][4] = '480'
                settings.users[call.message.chat.id][3] = '480'

            if call.data == 'video720':
                settings.users[call.message.chat.id][4] = '720'
                settings.users[call.message.chat.id][3] = '720'

            if call.data == 'shortvideo720':
                settings.users[call.message.chat.id][4] = '720'
                settings.users[call.message.chat.id][3] = '1080'

            if call.data == 'shortvideo240':
                settings.users[call.message.chat.id][4] = '240'
                settings.users[call.message.chat.id][3] = '360'

            if call.data == 'shortvideo360':
                settings.users[call.message.chat.id][4] = '360'
                settings.users[call.message.chat.id][3] = '480'

            if call.data == 'shortvideo480':
                settings.users[call.message.chat.id][4] = '480'
                settings.users[call.message.chat.id][3] = '720'

            if call.data == 'video1080':
                settings.users[call.message.chat.id][4] = '1080'
                settings.users[call.message.chat.id][3] = '1080'

            if call.data == 'audio':
                msg = await bot.send_message(chat_id=call.message.chat.id,
                                             text=text_translator(text=f'<b>Аудиофайл скачивается...\n\n'
                                                                       'Это может занять некоторое время.</b>',
                                                                  src="ru",
                                                                  dest=settings.users[call.message.chat.id][2]))
                YDL_OPTIONS = {
                    'max_filesize': 2000000000,
                    'format': 'bestaudio[filesize<50M]/bestaudio',
                    'outtmpl': settings.users[call.message.chat.id][1] + '.mp3',
                    'output': settings.users[call.message.chat.id][1] + '.mp3',
                    'quiet': True
                }

                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    try:
                        filename_collector = FilenameCollectorPP()
                        ydl.add_post_processor(filename_collector)
                        try:
                            video = ydl.extract_info(f"ytsearch:{settings.users[call.message.chat.id][0]}",
                                                     download=True)['entries'][0]
                        except IndexError:
                            video = ydl.extract_info(f"ytsearch:https://www.youtube.com/watch?v={settings.url_id}",
                                                     download=True)['entries'][0]

                        markup1 = types.InlineKeyboardMarkup(row_width=1)

                        choose = types.InlineKeyboardButton(text_translator(
                            text='Поиск нового видео',
                            src="ru",
                            dest=settings.users[call.message.chat.id][2]),
                            switch_inline_query_current_chat='')
                        markup1.add(choose)
                        if len(settings.users[call.message.chat.id][1] + '.mp3') != 4:
                            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id,
                                                        text=text_translator(text=f'<b>Аудиофайл загружается...</b>',
                                                                             src="ru",
                                                                             dest=settings.users[call.message.chat.id][
                                                                                 2]))
                            file_size = os.stat(settings.users[call.message.chat.id][1] + '.mp3').st_size
                            await bot.send_audio(chat_id=call.message.chat.id,
                                                 audio=open(settings.users[call.message.chat.id][1] + '.mp3', 'rb'),
                                                 caption=f"💾 {round(file_size / 1024 / 1024, 1)}MB, @yt_loadbot",
                                                 reply_markup=markup1)
                            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id,
                                                        text=text_translator(
                                                            text=f'<b>✅ Аудиофайл успешно загрузился.</b>',
                                                            src="ru",
                                                            dest=settings.users[call.message.chat.id][2]))
                            os.remove(settings.users[call.message.chat.id][1] + '.mp3')
                        else:
                            raise FileNotFoundError

                    except DownloadError:
                        raise FileNotFoundError

                    except FileNotFoundError:
                        await bot.edit_message_text(
                            chat_id=call.message.chat.id, message_id=msg.message_id,
                            text=text_translator(
                                text='<b>🚫 При загрузке аудиофайла произошла ошибка.\n\n'
                                     'Попробуйте снова послать боту ссылку с этим видеороликом.</b>',
                                src="ru",
                                dest=settings.users[call.message.chat.id][2]))
                        os.remove(settings.users[call.message.chat.id][1] + '.mp3')

                    except NetworkError:
                        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id,
                                                    text=text_translator(
                                                        text='<b>🚫 Загрузка провалилась :(</b>',
                                                        src="ru",
                                                        dest=settings.users[call.message.chat.id][2]))

                        await bot.send_message(call.message.chat.id, text_translator(
                            text='<b>Аудиофайл превысил лимит в 50 мб'
                                 '.</b>',
                            src="ru",
                            dest=settings.users[call.message.chat.id][2]))

                        if filename_collector.filenames:
                            os.remove(settings.users[call.message.chat.id][1] + '.mp3')

            if 'video' in call.data:
                YDL_OPTIONS = {}
                msg = await bot.send_message(chat_id=call.message.chat.id,
                                             text=text_translator(text=f'<b>Видеофайл скачивается...\n\n'
                                                                       'Это может занять некоторое время.</b>',
                                                                  src="ru",
                                                                  dest=settings.users[call.message.chat.id][2]))

                if 'shortvideo1080' in call.data:
                    YDL_OPTIONS = {
                        'max_filesize': 2000000000,
                        'format': f"(bestvideo[ext=mp4]+bestaudio[ext=m4a])[filesize<50M]/"
                                  f"bestvideo+bestaudio",
                        'outtmpl': settings.users[call.message.chat.id][1] + '.mp4',
                        'output': settings.users[call.message.chat.id][1] + '.mp4',
                        'quiet': True
                    }

                    settings.users[call.message.chat.id][4] = '1080'

                else:
                    YDL_OPTIONS = {
                        'max_filesize': 2000000000,
                        'format': f"(bestvideo[height<={settings.users[call.message.chat.id][3]}][ext=mp4]+"
                                  f"bestaudio[ext=m4a])[filesize<50M]/bestvideo+bestaudio",
                        'outtmpl': settings.users[call.message.chat.id][1] + '.mp4',
                        'output': settings.users[call.message.chat.id][1] + '.mp4',
                        'quiet': True
                    }

                with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                    try:
                        filename_collector = FilenameCollectorPP()
                        ydl.add_post_processor(filename_collector)
                        try:
                            video = ydl.extract_info(f"ytsearch:{settings.users[call.message.chat.id][0]}",
                                                     download=True)['entries'][0]
                        except IndexError:
                            video = ydl.extract_info(f"ytsearch:https://www.youtube.com/watch?v={settings.url_id}",
                                                     download=True)['entries'][0]

                        markup1 = types.InlineKeyboardMarkup(row_width=1)

                        choose = types.InlineKeyboardButton(
                            text_translator(text='Поиск нового видео', src="ru",
                                            dest=settings.users[call.message.chat.id][
                                                2]),
                            switch_inline_query_current_chat='')
                        markup1.add(choose)

                        if len(settings.users[call.message.chat.id][1] + '.mp4') != 4:
                            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id,
                                                        text=text_translator(text='<b>Видеофайл загружается...</b>',
                                                                             src="ru",
                                                                             dest=settings.users[call.message.chat.id][
                                                                                 2]))

                            file_size = os.stat(settings.users[call.message.chat.id][1] + '.mp4').st_size
                            await bot.send_video(chat_id=call.message.chat.id,
                                                 video=open(settings.users[call.message.chat.id][1] + '.mp4', 'rb'),
                                                 caption=f"{settings.users[call.message.chat.id][1]} \n\n"
                                                         f"💾 {round(file_size / 1024 / 1024, 1)}MB,"
                                                         f" 🎬{settings.users[call.message.chat.id][4]}p, @yt_loadbot",
                                                 reply_markup=markup1)

                            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id,
                                                        text=text_translator(
                                                            text=f'<b>✅ Видеофайл успешно загрузился.</b>',
                                                            src="ru",
                                                            dest=settings.users[call.message.chat.id][2]))
                            os.remove(settings.users[call.message.chat.id][1] + '.mp4')

                        else:
                            raise FileNotFoundError

                    except DownloadError:
                        raise FileNotFoundError

                    except FileNotFoundError:
                        await bot.edit_message_text(
                            chat_id=call.message.chat.id, message_id=msg.message_id,
                            text=text_translator(
                                text='<b>🚫 При загрузке видеофайла произошла ошибка.\n\n'
                                     'Попробуйте снова послать боту ссылку с этим видеороликом.</b>',
                                src="ru",
                                dest=settings.users[call.message.chat.id][2]))
                        try:
                            os.remove('.mp4.mp4')

                        except:
                            os.remove('.mp4.webm')

                    except IndexError:
                        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id,
                                                    text=text_translator(
                                                        text='<b>🚫 Загрузка провалилась :(</b>',
                                                        src="ru",
                                                        dest=settings.users[call.message.chat.id][2]))

                        await bot.send_message(call.message.chat.id, '<b>Видеофайл слишком большой!</b>')

                    except NetworkError:
                        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg.message_id,
                                                    text=text_translator(
                                                        text='<b>🚫 Загрузка провалилась :(</b>',
                                                        src="ru",
                                                        dest=settings.users[call.message.chat.id][2]))

                        await bot.send_message(call.message.chat.id, text_translator(
                            text='<b>Видеофайл превысил лимит в 50 мб'
                                 '.</b>',
                            src="ru",
                            dest=settings.users[call.message.chat.id][2]))

                        if filename_collector.filenames:
                            os.remove(settings.users[call.message.chat.id][1] + '.mp4')

            if call.data == 'cancel':
                await bot.delete_message(call.message.chat.id, message_id=call.message.message_id)

        except KeyError:
            await bot.send_message(call.message.chat.id, text="<b>The bot has been updated and needs to be restarted "
                                                              "(Бот обновился и требует перезапуск).\n\n 👉 /restart 👈"
                                                              "</b>")


def searcher(telegram):
    return YoutubeSearch(telegram, max_results=100).to_dict()


@dp.inline_handler()
async def inline_handler(query: types.InlineQuery):
    text = query.query or 'music'

    links = searcher(text)

    articles = [types.InlineQueryResultArticle(
        id=hashlib.md5(f'{link["id"]}'.encode()).hexdigest(),
        title=f'{link["title"]}',
        description=f"👤 {link['channel']} • {link['publish_time']} \n 👁"
                    f"{str(link['views'])[:str(link['views']).find('п')]}• 🕒 {link['duration']}",
        thumb_url=f'{link["thumbnails"][0]}',
        input_message_content=types.InputTextMessageContent(
            message_text=f'https://www.youtube.com/watch?v={link["id"]}'
        )

    ) for link in links]

    await query.answer(articles, cache_time=60, is_personal=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
